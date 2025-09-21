from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import openai
import os
from dotenv import load_dotenv
from models.database import DatabaseManager
from datetime import datetime
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize database manager
db_manager = DatabaseManager()

@app.route('/')
def index():
    """Homepage with topic input form"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_blog():
    """Generate blog content using OpenAI API"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({'error': 'Please provide a valid topic'}), 400
        
        # Create OpenAI prompt
        prompt = f"""
        Write a comprehensive, engaging blog post about "{topic}". 
        The blog post should be:
        - Well-structured with clear sections
        - Informative and engaging
        - Around 800-1200 words
        - Include an introduction, main content sections, and a conclusion
        - Use a professional but accessible tone
        
        Topic: {topic}
        """
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional blog writer who creates engaging, well-structured, and informative blog posts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        blog_content = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'topic': topic,
            'content': blog_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate blog: {str(e)}'}), 500

@app.route('/save', methods=['POST'])
def save_blog():
    """Save generated blog to MySQL database"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        content = data.get('content', '').strip()
        
        if not topic or not content:
            return jsonify({'error': 'Topic and content are required'}), 400
        
        # Save to database
        blog_id = db_manager.save_blog(topic, content)
        
        if blog_id:
            return jsonify({
                'success': True,
                'message': 'Blog saved successfully!',
                'blog_id': blog_id
            })
        else:
            return jsonify({'error': 'Failed to save blog to database'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to save blog: {str(e)}'}), 500

@app.route('/dashboard')
def dashboard():
    """Dashboard showing all saved blogs"""
    try:
        blogs = db_manager.get_all_blogs()
        return render_template('dashboard.html', blogs=blogs)
    except Exception as e:
        flash(f'Error loading blogs: {str(e)}', 'error')
        return render_template('dashboard.html', blogs=[])

@app.route('/blog/<int:blog_id>')
def view_blog(blog_id):
    """View individual blog post"""
    try:
        blog = db_manager.get_blog_by_id(blog_id)
        if blog:
            return render_template('blog_view.html', blog=blog)
        else:
            flash('Blog not found', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error loading blog: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/edit/<int:blog_id>', methods=['GET', 'POST'])
def edit_blog(blog_id):
    """Edit existing blog post"""
    try:
        if request.method == 'GET':
            blog = db_manager.get_blog_by_id(blog_id)
            if blog:
                return render_template('edit_blog.html', blog=blog)
            else:
                flash('Blog not found', 'error')
                return redirect(url_for('dashboard'))
        
        elif request.method == 'POST':
            data = request.get_json()
            topic = data.get('topic', '').strip()
            content = data.get('content', '').strip()
            
            if not topic or not content:
                return jsonify({'error': 'Topic and content are required'}), 400
            
            success = db_manager.update_blog(blog_id, topic, content)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Blog updated successfully!'
                })
            else:
                return jsonify({'error': 'Failed to update blog'}), 500
                
    except Exception as e:
        if request.method == 'POST':
            return jsonify({'error': f'Failed to update blog: {str(e)}'}), 500
        else:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

@app.route('/delete/<int:blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    """Delete blog post"""
    try:
        success = db_manager.delete_blog(blog_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Blog deleted successfully!'
            })
        else:
            return jsonify({'error': 'Failed to delete blog'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to delete blog: {str(e)}'}), 500

@app.route('/api/blogs')
def api_blogs():
    """API endpoint to get all blogs as JSON"""
    try:
        blogs = db_manager.get_all_blogs()
        return jsonify({'blogs': blogs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create database tables on startup
    db_manager.create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)