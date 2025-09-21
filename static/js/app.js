// AI Blog Generator - Frontend JavaScript

class BlogGenerator {
    constructor() {
        this.currentBlog = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.addAnimations();
    }

    bindEvents() {
        // Blog generation form
        const blogForm = document.getElementById('blogForm');
        if (blogForm) {
            blogForm.addEventListener('submit', this.handleBlogGeneration.bind(this));
        }

        // Save blog button
        const saveBlogBtn = document.getElementById('saveBlogBtn');
        if (saveBlogBtn) {
            saveBlogBtn.addEventListener('click', this.handleSaveBlog.bind(this));
        }

        // Regenerate blog button
        const regenerateBtn = document.getElementById('regenerateBtn');
        if (regenerateBtn) {
            regenerateBtn.addEventListener('click', this.handleRegenerate.bind(this));
        }

        // Add smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    addAnimations() {
        // Add fade-in animation to cards on page load
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('fade-in');
            }, index * 100);
        });

        // Add hover effects to feature icons
        const featureIcons = document.querySelectorAll('.feature-icon i');
        featureIcons.forEach(icon => {
            icon.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.2) rotate(10deg)';
            });
            
            icon.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1) rotate(0deg)';
            });
        });
    }

    async handleBlogGeneration(e) {
        e.preventDefault();
        
        const topicInput = document.getElementById('blogTopic');
        const topic = topicInput.value.trim();
        
        if (!topic) {
            this.showAlert('Please enter a blog topic', 'warning');
            topicInput.focus();
            return;
        }

        // Validate topic length
        if (topic.length < 3) {
            this.showAlert('Please enter a topic with at least 3 characters', 'warning');
            topicInput.focus();
            return;
        }

        if (topic.length > 200) {
            this.showAlert('Topic is too long. Please keep it under 200 characters', 'warning');
            topicInput.focus();
            return;
        }

        this.showLoading();
        this.hideAlerts();

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic: topic })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.currentBlog = {
                    topic: data.topic,
                    content: data.content
                };
                this.displayGeneratedBlog(data.topic, data.content);
                this.showAlert('Blog generated successfully!', 'success');
            } else {
                throw new Error(data.error || 'Failed to generate blog');
            }

        } catch (error) {
            console.error('Error generating blog:', error);
            this.showAlert(`Error: ${error.message}`, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async handleSaveBlog() {
        if (!this.currentBlog) {
            this.showAlert('No blog to save', 'warning');
            return;
        }

        const saveBlogBtn = document.getElementById('saveBlogBtn');
        const originalText = saveBlogBtn.innerHTML;
        
        // Show loading state
        saveBlogBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        saveBlogBtn.disabled = true;

        try {
            const response = await fetch('/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic: this.currentBlog.topic,
                    content: this.currentBlog.content
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showAlert(data.message, 'success');
                saveBlogBtn.innerHTML = '<i class="fas fa-check me-2"></i>Saved!';
                
                // Reset button after 2 seconds
                setTimeout(() => {
                    saveBlogBtn.innerHTML = originalText;
                    saveBlogBtn.disabled = false;
                }, 2000);
            } else {
                throw new Error(data.error || 'Failed to save blog');
            }

        } catch (error) {
            console.error('Error saving blog:', error);
            this.showAlert(`Error: ${error.message}`, 'danger');
            saveBlogBtn.innerHTML = originalText;
            saveBlogBtn.disabled = false;
        }
    }

    handleRegenerate() {
        const topicInput = document.getElementById('blogTopic');
        const topic = topicInput.value.trim();
        
        if (!topic) {
            this.showAlert('Please enter a topic first', 'warning');
            topicInput.focus();
            return;
        }

        // Confirm regeneration
        if (confirm('This will generate a new blog post for the same topic. Continue?')) {
            this.handleBlogGeneration({ preventDefault: () => {} });
        }
    }

    displayGeneratedBlog(topic, content) {
        const blogResult = document.getElementById('blogResult');
        const generatedTopic = document.getElementById('generatedTopic');
        const generatedContent = document.getElementById('generatedContent');

        generatedTopic.textContent = topic;
        generatedContent.innerHTML = this.formatBlogContent(content);

        blogResult.style.display = 'block';
        blogResult.classList.add('slide-up');

        // Scroll to results
        blogResult.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    formatBlogContent(content) {
        // Convert line breaks to HTML
        let formattedContent = content.replace(/\n\n/g, '</p><p>');
        formattedContent = formattedContent.replace(/\n/g, '<br>');
        
        // Wrap in paragraphs if not already formatted
        if (!formattedContent.includes('<p>')) {
            formattedContent = '<p>' + formattedContent + '</p>';
        }

        // Make headers bold if they're in the format "# Header" or "## Header"
        formattedContent = formattedContent.replace(/^(#{1,6})\s(.+)$/gm, function(match, hashes, text) {
            const level = hashes.length;
            return `<h${level} class="text-primary fw-bold mt-4 mb-3">${text}</h${level}>`;
        });

        // Make **bold** text bold
        formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Make *italic* text italic
        formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Convert bullet points
        formattedContent = formattedContent.replace(/^[-•]\s(.+)$/gm, '<li>$1</li>');
        formattedContent = formattedContent.replace(/(<li>.*<\/li>)/s, '<ul class="mb-3">$1</ul>');

        // Convert numbered lists
        formattedContent = formattedContent.replace(/^\d+\.\s(.+)$/gm, '<li>$1</li>');
        
        return formattedContent;
    }

    showLoading() {
        const loadingSection = document.getElementById('loadingSection');
        const generateBtn = document.getElementById('generateBtn');
        const blogResult = document.getElementById('blogResult');

        if (loadingSection) {
            loadingSection.style.display = 'block';
        }

        if (generateBtn) {
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
            generateBtn.disabled = true;
        }

        if (blogResult) {
            blogResult.style.display = 'none';
        }
    }

    hideLoading() {
        const loadingSection = document.getElementById('loadingSection');
        const generateBtn = document.getElementById('generateBtn');

        if (loadingSection) {
            loadingSection.style.display = 'none';
        }

        if (generateBtn) {
            generateBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles me-2"></i>Generate Blog Post';
            generateBtn.disabled = false;
        }
    }

    showAlert(message, type) {
        // Remove existing alerts first
        this.hideAlerts();

        const alertId = type === 'success' ? 'successAlert' : 'errorAlert';
        const messageId = type === 'success' ? 'successMessage' : 'errorMessage';
        
        const alertElement = document.getElementById(alertId);
        const messageElement = document.getElementById(messageId);

        if (alertElement && messageElement) {
            messageElement.textContent = message;
            alertElement.style.display = 'block';
            alertElement.classList.add('fade-in');

            // Auto-hide success messages
            if (type === 'success') {
                setTimeout(() => {
                    this.hideAlerts();
                }, 5000);
            }

            // Scroll to alert
            alertElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }
    }

    hideAlerts() {
        const successAlert = document.getElementById('successAlert');
        const errorAlert = document.getElementById('errorAlert');

        if (successAlert) {
            successAlert.style.display = 'none';
        }

        if (errorAlert) {
            errorAlert.style.display = 'none';
        }
    }

    // Utility method to copy text to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showAlert('Copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy text: ', err);
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                this.showAlert('Copied to clipboard!', 'success');
            } catch (fallbackErr) {
                this.showAlert('Failed to copy text', 'danger');
            }
            document.body.removeChild(textArea);
        }
    }

    // Method to validate input in real-time
    setupRealTimeValidation() {
        const topicInput = document.getElementById('blogTopic');
        if (topicInput) {
            topicInput.addEventListener('input', function() {
                const value = this.value.trim();
                const charCount = value.length;
                
                // Add character count display
                let charCountDiv = document.getElementById('charCount');
                if (!charCountDiv) {
                    charCountDiv = document.createElement('div');
                    charCountDiv.id = 'charCount';
                    charCountDiv.className = 'form-text';
                    this.parentNode.appendChild(charCountDiv);
                }
                
                charCountDiv.textContent = `${charCount}/200 characters`;
                
                if (charCount > 200) {
                    this.classList.add('is-invalid');
                    charCountDiv.classList.add('text-danger');
                } else if (charCount >= 3) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                    charCountDiv.classList.remove('text-danger');
                    charCountDiv.classList.add('text-success');
                } else {
                    this.classList.remove('is-invalid', 'is-valid');
                    charCountDiv.classList.remove('text-danger', 'text-success');
                }
            });
        }
    }
}

// Initialize the blog generator when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const blogGenerator = new BlogGenerator();
    blogGenerator.setupRealTimeValidation();

    // Add some UI enhancements
    
    // Smooth page transitions
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.3s ease-in-out';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);

    // Add loading overlay for page navigation
    const links = document.querySelectorAll('a:not([href^="#"]):not([href^="javascript:"]):not([target="_blank"])');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            // Only add loading for same-origin links
            if (this.hostname === window.location.hostname) {
                document.body.style.opacity = '0.7';
            }
        });
    });

    // Handle browser back/forward buttons
    window.addEventListener('pageshow', function(e) {
        if (e.persisted) {
            document.body.style.opacity = '1';
        }
    });

    console.log('AI Blog Generator initialized successfully!');
});