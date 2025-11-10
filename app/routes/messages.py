from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.message import Message
from datetime import datetime

message_bp = Blueprint('messages', __name__, url_prefix='/messages')


@message_bp.route('/')
@login_required
def inbox():
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).all()
    unread_count = Message.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    return render_template('messages/inbox.html', messages=messages, unread_count=unread_count)


@message_bp.route('/sent')
@login_required
def sent():
    messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc()).all()
    return render_template('messages/sent.html', messages=messages)


@message_bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        message = Message(
            subject=subject,
            body=body,
            sender_id=current_user.id,
            recipient_id=int(recipient_id)
        )
        
        try:
            db.session.add(message)
            db.session.commit()
            flash('Message sent successfully!', 'success')
            return redirect(url_for('messages.sent'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error sending message: {str(e)}', 'danger')
    
    users = User.query.filter(User.id != current_user.id, User.is_active == True).all()
    return render_template('messages/compose.html', users=users)


@message_bp.route('/<int:id>')
@login_required
def view_message(id):
    message = Message.query.get_or_404(id)
    
    if message.recipient_id != current_user.id and message.sender_id != current_user.id:
        flash('You do not have permission to view this message.', 'danger')
        return redirect(url_for('messages.inbox'))
    
    if message.recipient_id == current_user.id and not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return render_template('messages/view.html', message=message)


@message_bp.route('/<int:id>/reply', methods=['GET', 'POST'])
@login_required
def reply(id):
    original_message = Message.query.get_or_404(id)
    
    if original_message.recipient_id != current_user.id:
        flash('You can only reply to messages sent to you.', 'danger')
        return redirect(url_for('messages.inbox'))
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        message = Message(
            subject=subject,
            body=body,
            sender_id=current_user.id,
            recipient_id=original_message.sender_id
        )
        
        try:
            db.session.add(message)
            db.session.commit()
            flash('Reply sent successfully!', 'success')
            return redirect(url_for('messages.inbox'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error sending reply: {str(e)}', 'danger')
    
    return render_template('messages/reply.html', original_message=original_message)
