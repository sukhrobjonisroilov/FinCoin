#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan


# Bu faylda Faqatgina Cartalar bilan bog'liq bo'lgan o'tqazma va bonuslar uchun codelar yoziladi. Asosan o'tqazmalar
from contextlib import closing

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.shortcuts import redirect, render
from methodism import generate_key

from base.custom import permission_checker, admin_permission_checker, user_notification_sender
from base.errors import MSG
from base.helper import lang_helper, make_transfer
from core.models import Card, Token
from core.models.monitoring import Monitoring


@permission_checker
def award(request, pk=None):
    if request.POST:
        sql = f"""
            UPDATE core_card 
            set balance = balance + {request.POST.get('reward', 0)}
            {f'where user_id = {pk} ' if pk else ""}
        """
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql)
    user_notification_sender(user_id=pk, note=request.POST.get('desc_reward', 0), bonus=request.POST.get('reward', 0),
                             type="Bonus", many=pk is None)

    if pk:
        return redirect("get_user_info", pk=pk)
    else:
        return redirect("home")


@login_required(login_url="login")
def p2p(request, status=None):
    sender_card = Card.objects.filter(user=request.user).first()
    ctx = {
        'card_user': sender_card
    }
    if request.method == 'POST':
        if status == 'p2p':
            if sender_card.balance < int(request.POST.get('amount', 0)) or int(request.POST.get('amount', 0)) <= 1000:
                ctx.update({"error": MSG['BalanceInfluence'][lang_helper(request)]})
                return render(request, 'sidebars/payments.html', ctx)
            reciever_card = Card.objects.filter(token=request.session.get('receiver', {}).get("token")).first()
            try:
                data = {
                    "tr_id": generate_key(50),
                    'sender': sender_card,
                    'sender_token': sender_card.token,
                    'receiver': reciever_card,
                    'receiver_token': reciever_card.token,
                    'amount': int(request.POST.get('amount', 0)),
                }
            except:
                return redirect("user_payments")
            monitoring = Monitoring.objects.create(**data)
            monitoring.status = 1 if make_transfer(sender_card, reciever_card,
                                                   int(request.POST.get('amount', 0))) else 2
            monitoring.save()
            if monitoring.status == 1:
                amount = int(request.POST.get('amount', 0))
                print(amount, amount*-1)
                user_notification_sender(sender_card.user_id, "User Transfer", "p2p", bonus=amount*-1)
                user_notification_sender(reciever_card.user_id, "User Transfer", "p2p", bonus=amount)
            ctx.update({"success": MSG['SuccessTransaction'][lang_helper(request)]})
            try:
                del request.session['receiver']
                del request.session['tr_status']
            except:
                pass
            return render(request, 'sidebars/payments.html', ctx)

        reciever_card = Card.objects.filter(number=request.POST.get("receiver")).first()

        if not reciever_card:
            ctx.update({"error": MSG['ReceiverCardNotFound'][lang_helper(request)]})
            return render(request, 'sidebars/payments.html', ctx)
        if reciever_card.blocked:
            ctx.update({"error": MSG['TransferToReceiverDenied'][lang_helper(request)]})
            return render(request, 'sidebars/payments.html', ctx)
        if sender_card == reciever_card:
            ctx.update({"error": MSG['TransferToReceiverDenied'][lang_helper(request)]})
            return render(request, 'sidebars/payments.html', ctx)

        request.session['receiver'] = reciever_card.response()
        request.session['tr_status'] = "p2p"
    else:
        try:
            del request.session['receiver']
            del request.session['tr_status']
        except:
            pass
    return render(request, 'sidebars/payments.html', ctx)


@login_required(login_url='login')
def monitoring_page(request):
    if request.user.ut == 3:
        cart = Card.objects.filter(user_id=request.user.id).first()
        all_ = Monitoring.objects.filter(Q(sender_id=cart.id) | Q(receiver_id=cart.id)).order_by('-id')
    else:
        all_ = Monitoring.objects.all().order_by('-id')
    paginator = Paginator(all_, 50)
    page_number = request.GET.get("page", 1)
    paginated = paginator.get_page(page_number)
    ctx = {"monitorings": paginated}
    return render(request, 'pages/monitoring.html', ctx)
