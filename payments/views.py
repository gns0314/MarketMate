from django.conf import settings
from main.env import config
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import PaymentResult,Buyer
from iamport import Iamport
import json
import requests



def getToken():
    url = 'https://api.iamport.kr/users/getToken'

    headers = {'Content-Type': 'application/json', 'charset': 'UTF-8', 'Accept': '*/*'}
    body = {
        'imp_key': config('IMP_KEY', default=None), # REST API Key
        'imp_secret': config('IMP_SECRET', default=None) # REST API Secret
    }

    try:
        response = json.loads(requests.post(url, headers=headers, data=json.dumps(body, ensure_ascii=False, indent="\t")).text)['response']['access_token']
        return response
    except Exception as ex:
        return ex

class PaymentInfoView(APIView):
    def post(self, request):
        iamport = Iamport(
            imp_key=settings.IAMPORT_KEY,
            imp_secret=settings.IAMPORT_SECRET
        )
        
        merchant_uid = request.data.get("merchant_uid")
        if not merchant_uid:
            return Response({"error": "merchant_uid is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = request.user
            if not user.is_authenticated:
                return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)
            
            # 이메일 값을 사용하여 Buyer 객체 조회
            buyer = Buyer.objects.get(email=user.email)
            print(buyer)
            response = iamport.find(merchant_uid=merchant_uid)
            print(response)
            imp_uid = response.get("imp_uid")
            merchant_uid = response.get("merchant_uid")
            amount = response.get("amount")
            payment_status = response.get("status")  
            
            # 추출한 정보를 DB에 저장
            PaymentResult.objects.create(
                buyer=buyer,
                imp_uid=imp_uid,
                merchant_uid=merchant_uid,
                amount=amount,
                status=payment_status,  
            )
            return Response({"message": "Payment data saved successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

def performRefund(token, imp_uid, amount):
    url = f"https://api.iamport.kr/payments/cancel"
    
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    data = {
        'imp_uid': imp_uid,
        'amount': amount
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        
        if response_data['code'] == 0:
            return 'success'
        else:
            return 'failed'
    except Exception as ex:
        return 'failed'


# 환불
class RefundView(APIView):
    # permission_classes = [IsAuthenticated, IsBuyer]

    def post(self, request):
        purchase = get_object_or_404(PaymentResult, merchant_uid=request.data.get('merchant_uid'))

        if purchase.status != 'refunded':
            token = getToken()

            # 환불 로직 추가
            refund_result = performRefund(token, purchase.merchant_uid, purchase.price)
            if refund_result == 'success':
                # 환불 처리 성공 시 업데이트
                purchase.status = 'refunded'
                purchase.save()

                # 주문 및 상품 업데이트 로직 추가
                order = purchase.order
                order.status = 'refunded'
                order.save()

                product = order.product
                product.amount += 1
                product.save()

                return Response({'message': 'Refund successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Refund failed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Already refunded'}, status=status.HTTP_400_BAD_REQUEST)