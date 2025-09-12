from flask import Flask, request, jsonify
import sys
import os
import json
from typing import List, Dict, Any

# Add the django_dr1_app path to sys.path to import the embedder
sys.path.append(os.path.join(os.path.dirname(__file__), 'django_dr1_app', 'db_action'))
from embeder import QwenInstruct

app = Flask(__name__)

# Initialize the QwenInstruct embedder
# You can modify the model_path as needed
MODEL_PATH = "../local_models/gte-Qwen2-1.5B-instruct"  # Default model path, can be changed
embedder = None

def initialize_embedder():
    """Initialize the QwenInstruct embedder"""
    global embedder
    try:
        embedder = QwenInstruct(MODEL_PATH)
        print(f"Successfully initialized QwenInstruct with model: {MODEL_PATH}")
    except Exception as e:
        print(f"Error initializing embedder: {e}")
        # Fallback to a different model or handle the error
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint that actually tests system functionality"""
    health_status = {
        "status": "healthy",
        "service": "embedding-service",
        "model": MODEL_PATH,
        "checks": {}
    }
    
    # Check 1: Embedder initialization
    if embedder is None:
        health_status["status"] = "unhealthy"
        health_status["checks"]["embedder_initialized"] = {
            "status": "failed",
            "error": "Embedder not initialized"
        }
        return jsonify(health_status), 503
    else:
        health_status["checks"]["embedder_initialized"] = {
            "status": "passed",
            "message": "Embedder is initialized"
        }
    
    # Check 2: Test embedding functionality
    try:
        test_text = "This is a test text for health check"
        test_embeddings = embedder.embed_documents([test_text])
        
        if test_embeddings and len(test_embeddings) > 0:
            embedding_dim = len(test_embeddings[0])
            health_status["checks"]["embedding_functionality"] = {
                "status": "passed",
                "message": f"Embedding test successful, dimension: {embedding_dim}",
                "embedding_dimension": embedding_dim
            }
        else:
            health_status["status"] = "unhealthy"
            health_status["checks"]["embedding_functionality"] = {
                "status": "failed",
                "error": "Embedding test returned empty result"
            }
            return jsonify(health_status), 503
            
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["embedding_functionality"] = {
            "status": "failed",
            "error": f"Embedding test failed: {str(e)}"
        }
        return jsonify(health_status), 503
    
    # Check 3: Memory usage (optional)
    try:
        import psutil
        memory_info = psutil.virtual_memory()
        health_status["checks"]["memory_usage"] = {
            "status": "passed",
            "message": "Memory usage normal",
            "memory_percent": memory_info.percent,
            "available_mb": round(memory_info.available / 1024 / 1024, 2)
        }
        
        # Warn if memory usage is high
        if memory_info.percent > 90:
            health_status["checks"]["memory_usage"]["status"] = "warning"
            health_status["checks"]["memory_usage"]["message"] = "High memory usage detected"
            
    except ImportError:
        health_status["checks"]["memory_usage"] = {
            "status": "skipped",
            "message": "psutil not available for memory monitoring"
        }
    except Exception as e:
        health_status["checks"]["memory_usage"] = {
            "status": "failed",
            "error": f"Memory check failed: {str(e)}"
        }
    
    # Check 4: Model file accessibility
    try:
        if os.path.exists(MODEL_PATH):
            health_status["checks"]["model_accessibility"] = {
                "status": "passed",
                "message": "Model path is accessible"
            }
        else:
            health_status["status"] = "unhealthy"
            health_status["checks"]["model_accessibility"] = {
                "status": "failed",
                "error": f"Model path not found: {MODEL_PATH}"
            }
            return jsonify(health_status), 503
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["model_accessibility"] = {
            "status": "failed",
            "error": f"Model accessibility check failed: {str(e)}"
        }
        return jsonify(health_status), 503
    
    # Add timestamp
    from datetime import datetime
    health_status["timestamp"] = datetime.now().isoformat()
    
    return jsonify(health_status)

@app.route('/embed', methods=['POST'])
def embed_texts():
    """
    Embed a list of texts using QwenInstruct
    
    Expected JSON input:
    {
        "texts": ["text1", "text2", "text3"],
        "embedding_type": "documents"  # or "query"
    }
    
    Returns:
    {
        "embeddings": [[float, float, ...], [float, float, ...], ...],
        "text_count": 3,
        "embedding_dimension": 1024
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract texts and embedding type
        texts = data.get('texts', [])
        embedding_type = data.get('embedding_type', 'documents')
        
        # Validate input
        if not texts:
            return jsonify({"error": "No texts provided"}), 400
        
        if not isinstance(texts, list):
            return jsonify({"error": "Texts must be a list"}), 400
        
        if not all(isinstance(text, str) for text in texts):
            return jsonify({"error": "All texts must be strings"}), 400
        
        # Check if embedder is initialized
        if embedder is None:
            return jsonify({"error": "Embedder not initialized"}), 500
        
        # Generate embeddings based on type
        if embedding_type == 'query':
            embeddings = embedder.embed_query(texts)
        else:  # documents
            embeddings = embedder.embed_documents(texts)
        
        # Convert numpy arrays to lists for JSON serialization
        embeddings_list = [embedding.tolist() if hasattr(embedding, 'tolist') else embedding for embedding in embeddings]
        
        # Get embedding dimension
        embedding_dimension = len(embeddings_list[0]) if embeddings_list else 0
        
        return jsonify({
            "embeddings": embeddings_list,
            "text_count": len(texts),
            "embedding_dimension": embedding_dimension,
            "embedding_type": embedding_type
        })
        
    except Exception as e:
        return jsonify({"error": f"Embedding failed: {str(e)}"}), 500

@app.route('/embed_single', methods=['POST'])
def embed_single_text():
    """
    Embed a single text using QwenInstruct
    
    Expected JSON input:
    {
        "text": "single text to embed",
        "embedding_type": "documents"  # or "query"
    }
    
    Returns:
    {
        "embedding": [float, float, ...],
        "embedding_dimension": 1024
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract text and embedding type
        text = data.get('text', '')
        embedding_type = data.get('embedding_type', 'documents')
        
        # Validate input
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        if not isinstance(text, str):
            return jsonify({"error": "Text must be a string"}), 400
        
        # Check if embedder is initialized
        if embedder is None:
            return jsonify({"error": "Embedder not initialized"}), 500
        
        # Generate embedding based on type
        if embedding_type == 'query':
            embeddings = embedder.embed_query([text])
        else:  # documents
            embeddings = embedder.embed_documents([text])
        
        # Get the first (and only) embedding
        embedding = embeddings[0]
        
        # Convert numpy array to list for JSON serialization
        embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        
        return jsonify({
            "embedding": embedding_list,
            "embedding_dimension": len(embedding_list),
            "embedding_type": embedding_type
        })
        
    except Exception as e:
        return jsonify({"error": f"Embedding failed: {str(e)}"}), 500

@app.route('/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        "model_path": MODEL_PATH,
        "embedder_initialized": embedder is not None
    })

@app.route('/config', methods=['POST'])
def update_config():
    """Update configuration (restart required)"""
    global MODEL_PATH
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        new_model_path = data.get('model_path')
        if new_model_path:
            MODEL_PATH = new_model_path
            return jsonify({
                "message": "Configuration updated. Please restart the service to apply changes.",
                "new_model_path": MODEL_PATH
            })
        else:
            return jsonify({"error": "No model_path provided"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Configuration update failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Initialize the embedder when starting the service
    try:
        initialize_embedder()
        print("Embedding service started successfully!")
        print(f"Model: {MODEL_PATH}")
        print("Available endpoints:")
        print("  GET  /health - Health check")
        print("  POST /embed - Embed multiple texts")
        print("  POST /embed_single - Embed single text")
        print("  GET  /config - Get configuration")
        print("  POST /config - Update configuration")
    except Exception as e:
        print(f"Failed to initialize embedder: {e}")
        print("Service will start but embedding endpoints will return errors")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=4098, debug=False)