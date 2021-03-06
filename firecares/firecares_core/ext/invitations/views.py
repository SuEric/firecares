import json
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponse
from django.template.context import RequestContext
from django.utils import timezone
from django.views.generic import DeleteView
from django.http.response import JsonResponse
from invitations import signals
from invitations.adapters import get_invitations_adapter
from invitations.exceptions import AlreadyInvited, AlreadyAccepted, UserRegisteredEmail
from invitations.forms import CleanEmailMixin
from invitations.models import Invitation
from invitations.views import SendJSONInvite, AcceptInvite
from firecares.firecares_core.ext.registration.views import SESSION_EMAIL_WHITELISTED
from firecares.firestation.models import FireDepartment


def send_invitation(self, request, **kwargs):
    current_site = (kwargs['site'] if 'site' in kwargs
                    else Site.objects.get_current())
    invite_url = reverse('invitations:accept-invite',
                         args=[self.key])
    invite_url = request.build_absolute_uri(invite_url)

    ctx = RequestContext(request, {
        'invite_url': invite_url,
        'site_name': current_site.name,
        'email': self.email,
        'key': self.key,
        'inviter': self.inviter.email or 'a FireCARES department administrator',
        'department': self.departmentinvitation.department
    })

    email_template = 'invitations/email/email_invite'

    get_invitations_adapter().send_mail(
        email_template,
        self.email,
        ctx)
    self.sent = timezone.now()
    self.save()

    signals.invite_url_sent.send(
        sender=self.__class__,
        instance=self,
        invite_url_sent=invite_url,
        inviter=self.inviter)


# Monkey-patch the invitation model to inject additional email context
Invitation.send_invitation = send_invitation


def send_invites(invites, request):
    status_code = 400
    response = {'valid': [], 'invalid': []}
    if isinstance(invites, list):
        for invite in invites:
            try:
                invitee = invite.get('email')
                dept_id = int(invite.get('department_id'))

                validate_email(invitee)
                CleanEmailMixin().validate_invitation(invitee)

                dept = FireDepartment.objects.get(id=dept_id)
                if not dept.is_admin(request.user):
                    raise PermissionDenied()

                i = Invitation.create(invitee, inviter=request.user)
                i.departmentinvitation.department = dept
                i.departmentinvitation.save()
            except(ValueError, KeyError):
                pass
            except(PermissionDenied):
                status_code = 401
            except(ValidationError):
                response['invalid'].append({
                    invitee: 'Invalid email address'})
            except(AlreadyAccepted):
                response['invalid'].append({
                    invitee: 'A user with this email has already accepted'})
            except(AlreadyInvited):
                response['invalid'].append(
                    {invitee: 'An invite has already been sent for this user'})
            except(UserRegisteredEmail):
                response['invalid'].append(
                    {invitee: 'A registered user with this email address already exists'})
            else:
                i.send_invitation(request)
                response['valid'].append({invitee: 'invited'})

    if response['valid']:
        status_code = 201

    return response, status_code


class SendJSONDepartmentInvite(SendJSONInvite):
    def post(self, request, *args, **kwargs):
        invites = json.loads(request.body.decode())

        response, status_code = send_invites(invites, request)

        return HttpResponse(
            json.dumps(response),
            status=status_code, content_type='application/json')


class AcceptDepartmentInvite(AcceptInvite):
    def post(self, request, *args, **kwargs):
        ret = super(AcceptDepartmentInvite, self).post(self, request, *args, **kwargs)
        # AOK to proceed if the email address was stashed, allow for preregistration check bypass
        if 'account_verified_email' in request.session and request.session['account_verified_email']:
            request.session[SESSION_EMAIL_WHITELISTED] = request.session['account_verified_email']
        return ret


class CancelInvite(DeleteView):
    model = Invitation
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        dept = self.object.departmentinvitation.department
        if not dept.is_admin(request.user) or self.object.accepted:
            status_code = 401
        else:
            status_code = 200
            self.object.delete()
        return JsonResponse({}, status=status_code)
