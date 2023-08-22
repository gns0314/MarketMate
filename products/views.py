from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token

from users.models import Buyer, Seller
from .models import Product
from .serializers import ProductSerializer


# Create your views here.
class ProductList(APIView):
    # 상품 리스트 조회
    def get(self, request):
        products = Product.objects.all()

        if products:
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif not products:
            return Response("등록된 상품이 없습니다.")
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 상품 등록
    def post(self, request):
        seller =  get_object_or_404(Seller, pk=Token.objects.get(key=request.auth).user_id)

        if seller:
            request_data = request.data.copy()
            request_data['seller'] = seller.pk
            serializer = ProductSerializer(data=request_data)

            if serializer.is_valid():        
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            


# class ProductDetail(APIView):
#     # 상품 상세 정보
#     def get(self,request):

#     # 등록 상품 수정