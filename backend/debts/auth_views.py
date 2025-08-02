# debts/auth_views.py - Simplified version
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
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


class UserLoginView(TokenObtainPairView):
    """Obtain JWT access and refresh tokens"""
    permission_classes = [permissions.AllowAny]


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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get user profile details"""
    user = request.user
    profile_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
    return Response(profile_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """Change user password"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')

    if not all([old_password, new_password, new_password_confirm]):
        return Response({'error': 'All password fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != new_password_confirm:
        return Response({'error': 'New passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(old_password):
        return Response({'error': 'Old password is not correct'}, status=status.HTTP_400_BAD_REQUEST)

    # Django's set_password handles hashing and security
    user.set_password(new_password)
    user.save()

    # Logout user from all sessions (optional, but good for security after password change)
    # You might want to do this to invalidate old JWT refresh tokens too,
    # though simplejwt has its own blacklisting mechanism.
    # update_session_auth_hash(request, user) # This is for session authentication

    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Simple logout - delete token"""
    try:
        # If using Simple JWT, tokens are usually self-contained and don't need deletion here
        # Logout in JWT usually means blacklisting the refresh token.
        # This current logout logic is for Django REST Framework's TokenAuthentication
        # or clearing session. For Simple JWT, a separate logout mechanism (blacklist) is used.
        # This part of the code might need review if you solely rely on Simple JWT.
        # For now, it will likely raise an AttributeError as auth_token won't exist for JWT users.
        # request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out! (Note: For JWT, consider blacklisting refresh token)'}, status=status.HTTP_200_OK)
    except AttributeError: # Catches if auth_token does not exist (e.g., when using JWT)
        return Response({'message': 'Logged out (no token to delete, likely JWT user).'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': f'Error during logout: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_health_check(request):
    """Health check"""
    return Response({
        'status': 'healthy',
        'authenticated': request.user.is_authenticated,
        'user': request.user.username if request.user.is_authenticated else None
    })
