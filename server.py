"""Flask webhook server for Zalo Bot
Receives webhook events from Zalo and processes them using the bot."""

import os
import logging
from flask import Flask, request, jsonify
from zalokit.client import ZaloClient
from examples.zalo_bot_demo import InteractiveZaloBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Get credentials from environment variables
APP_ID = os.getenv('ZALO_APP_ID')
SECRET_KEY = os.getenv('ZALO_SECRET_KEY')
OFFICIAL_ACCOUNT_ID = os.getenv('ZALO_OA_ID')

# Validate required environment variables
if not all([APP_ID, SECRET_KEY, OFFICIAL_ACCOUNT_ID]):
    logger.error('Missing required environment variables!')
    logger.error('Please set: ZALO_APP_ID, ZALO_SECRET_KEY, ZALO_OA_ID')
    raise ValueError('Missing required environment variables')

# Initialize Zalo client and bot
try:
    zalo_client = ZaloClient(app_id=APP_ID, secret_key=SECRET_KEY)
    bot = InteractiveZaloBot(zalo_client=zalo_client, oa_id=OFFICIAL_ACCOUNT_ID)
    logger.info('Zalo bot initialized successfully')
except Exception as e:
    logger.error(f'Failed to initialize bot: {str(e)}')
    raise

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Handle Zalo webhook requests"""
    
    if request.method == 'GET':
        # Webhook verification from Zalo
        return jsonify({'status': 'ok', 'message': 'Webhook is active'})
    
    try:
        # Parse incoming webhook data
        data = request.json
        logger.info(f'Received webhook: {data}')
        
        # Extract event type and data
        event_name = data.get('event_name')
        
        if event_name == 'user_send_text':
            # Extract user message
            sender = data.get('sender', {})
            user_id = sender.get('id')
            message = data.get('message', {})
            text = message.get('text', '')
            
            logger.info(f'Message from {user_id}: {text}')
            
            # Process message with bot
            response = bot.process_message(user_id=user_id, message=text)
            
            if response:
                logger.info(f'Bot response: {response}')
                return jsonify({'status': 'success', 'response': response})
            else:
                logger.warning('Bot returned no response')
                return jsonify({'status': 'no_response'})
        
        elif event_name == 'user_received_message':
            # Message delivery confirmation
            logger.info('Message delivered successfully')
            return jsonify({'status': 'ok'})
        
        elif event_name == 'user_seen_message':
            # Message seen confirmation
            logger.info('Message seen by user')
            return jsonify({'status': 'ok'})
        
        else:
            logger.info(f'Unhandled event type: {event_name}')
            return jsonify({'status': 'ok', 'message': 'Event received'})
    
    except Exception as e:
        logger.error(f'Error processing webhook: {str(e)}', exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'zalo-bot-webhook',
        'bot_ready': bot is not None
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'ZaloKit Bot Server',
        'status': 'running',
        'endpoints': {
            'webhook': '/webhook',
            'health': '/health'
        }
    })

if __name__ == '__main__':
    # Get port from environment variable (for Railway/Heroku)
    port = int(os.getenv('PORT', 5000))
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False in production
    )
