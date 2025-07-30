# debts/auth_views.py - Simplified version
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Sum
from decimal import Decimal


class UserRegistrationView(APIView):
    """Simple user registration"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        
        # Basic validation
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        if User.objects.filter(username=data['username']).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        try:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            
            # Create token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'User registered successfully!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """Simple user login"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'token': token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """Simple user dashboard"""
    user = request.user
    
    # Import here to avoid circular imports
    from .models import Debt
    
    user_debts = Debt.objects.filter(creditor=user)
    
    total_owed = user_debts.filter(status='active').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    dashboard_data = {
        'user_info': {
            'id': user.id,
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'email': user.email,
        },
        'debt_summary': {
            'total_owed_to_me': total_owed,
            'total_debts_count': user_debts.count(),
            'active_debts_count': user_debts.filter(status='active').count(),
            'paid_debts_count': user_debts.filter(status='paid').count(),
        }
    }
    
    return Response(dashboard_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Simple logout - delete token"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out!'}, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Logged out!'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_health_check(request):
    """Health check"""
    return Response({
        'status': 'healthy',
        'authenticated': request.user.is_authenticated,
        'user': request.user.username if request.user.is_authenticated else None
    })