"""
View for handling user suggestions on composers and works.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
import json


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_suggestion(request):
    """
    Handle submission of user suggestions for composers or works.
    
    POST /api/suggestions/
    Body: {
        "item_type": "composer" or "work",
        "item_id": 123,
        "original_data": {...},
        "suggested_data": {...},
        "comment": "optional comment"
    }
    """
    item_type = request.data.get('item_type')
    item_id = request.data.get('item_id')
    original_data = request.data.get('original_data', {})
    suggested_data = request.data.get('suggested_data', {})
    comment = request.data.get('comment', '')
    
    if not item_type or not item_id:
        return Response(
            {'error': 'item_type and item_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Build email content
    subject = f'Suggestion for {item_type.capitalize()} #{item_id}'
    
    # Format the changes
    changes_text = []
    for key in suggested_data:
        original_value = original_data.get(key, 'N/A')
        suggested_value = suggested_data.get(key, 'N/A')
        
        # Handle nested objects (like country)
        if isinstance(original_value, dict):
            original_value = original_value.get('name', str(original_value))
        if isinstance(suggested_value, dict):
            suggested_value = suggested_value.get('name', str(suggested_value))
        
        if str(original_value) != str(suggested_value):
            changes_text.append(f"{key}:\n  Original: {original_value}\n  Suggested: {suggested_value}")
    
    message = f"""
New suggestion received for {item_type.capitalize()} ID: {item_id}

Item Name: {original_data.get('full_name') or original_data.get('title', 'Unknown')}

SUGGESTED CHANGES:
{chr(10).join(changes_text) if changes_text else 'No field changes detected'}

{f'COMMENT:{chr(10)}{comment}{chr(10)}' if comment else ''}

---
View at: http://127.0.0.1:8000/admin/music/{item_type}/{item_id}/change/

Original Data:
{json.dumps(original_data, indent=2)}

Suggested Data:
{json.dumps(suggested_data, indent=2)}
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,  # Don't crash if email fails in production
        )
        
        return Response({
            'message': 'Suggestion submitted successfully',
            'status': 'sent'
        })
    except Exception as e:
        print(f"Error sending email: {e}")
        # Still return success - the suggestion was received even if email failed
        return Response({
            'message': 'Suggestion received (email notification failed)',
            'status': 'received'
        })
