// Theme toggle functionality
function setTheme(theme) {
    try {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    } catch (error) {
        console.error('Error setting theme:', error);
    }
}

function toggleTheme() {
    try {
        const currentTheme = localStorage.getItem('theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        updateThemeIcon(newTheme);
    } catch (error) {
        console.error('Error toggling theme:', error);
    }
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fas fa-star' : 'fas fa-moon';
    } else {
        console.warn('Theme icon not found');
    }
}

// Cart functionality
let cart = JSON.parse(localStorage.getItem('cart')) || [];

function updateCartBadge() {
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
        cartBadge.textContent = cart.length;
        cartBadge.style.display = cart.length > 0 ? 'block' : 'none';
    } else {
        console.warn('Cart badge not found');
    }
}

function addToCart(product) {
    try {
        cart.push(product);
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartBadge();
        updateCartModal();
    } catch (error) {
        console.error('Error adding to cart:', error);
    }
}

function clearCart() {
    try {
        cart = [];
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartBadge();
        updateCartModal();
    } catch (error) {
        console.error('Error clearing cart:', error);
    }
}

function updateCartModal() {
    const cartItems = document.getElementById('cartItems');
    const cartEmpty = document.getElementById('cartEmpty');
    if (cartItems && cartEmpty) {
        cartItems.innerHTML = ''; // Clear existing content
        if (cart.length === 0) {
            cartEmpty.style.display = 'block';
        } else {
            cartEmpty.style.display = 'none';
            cart.forEach(item => {
                const div = document.createElement('div');
                div.className = 'cart-item';
                div.innerHTML = `<p>${item.name} - $${item.price}</p>`;
                cartItems.appendChild(div);
            });
        }
    } else {
        console.warn('Cart items or empty message element not found');
    }
}

// Product detail zoom
function initProductZoom() {
    const productImage = document.getElementById('productImage');
    if (productImage) {
        let isZoomed = false;

        // Click to toggle zoom
        productImage.addEventListener('click', () => {
            isZoomed = !isZoomed;
            productImage.classList.toggle('zoomed', isZoomed);
            productImage.style.cursor = isZoomed ? 'zoom-out' : 'zoom-in';
        });

        // Pinch zoom for mobile
        let scale = 1;
        let startDistance = 0;

        productImage.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                startDistance = Math.hypot(
                    e.touches[0].pageX - e.touches[1].pageX,
                    e.touches[0].pageY - e.touches[1].pageY
                );
            }
        });

        productImage.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2) {
                e.preventDefault();
                const currentDistance = Math.hypot(
                    e.touches[0].pageX - e.touches[1].pageX,
                    e.touches[0].pageY - e.touches[1].pageY
                );
                scale = (currentDistance / startDistance) * 1;
                scale = Math.min(Math.max(1, scale), 2);
                productImage.style.transform = `scale(${scale})`;
            }
        });

        productImage.addEventListener('touchend', () => {
            if (scale <= 1) {
                isZoomed = false;
                productImage.classList.remove('zoomed');
                productImage.style.transform = 'scale(1)';
                productImage.style.cursor = 'zoom-in';
            }
        });
    } else {
        console.warn('Product image not found for zoom');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    try {
        const savedTheme = localStorage.getItem('theme') || 'light';
        setTheme(savedTheme);
        updateThemeIcon(savedTheme);
        updateCartBadge();
        updateCartModal();

        // Initialize product zoom
        if (document.getElementById('productImage')) {
            initProductZoom();
        }

        // Add to cart buttons
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', () => {
                const product = {
                    id: button.dataset.productId,
                    name: button.dataset.productName,
                    price: button.dataset.productPrice
                };
                if (product.id && product.name && product.price) {
                    addToCart(product);
                } else {
                    console.error('Invalid product data:', product);
                }
            });
        });

        // Clear cart button
        const clearCartBtn = document.getElementById('clearCart');
        if (clearCartBtn) {
            clearCartBtn.addEventListener('click', clearCart);
        } else {
            console.warn('Clear cart button not found');
        }

        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            const href = anchor.getAttribute('href');
            if (href && href !== '#') { // Skip invalid or empty href
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth'
                        });
                    }
                });
            }
        });

        // Cart modal
        const cartIcon = document.querySelector('.cart-icon');
        if (cartIcon) {
            cartIcon.addEventListener('click', () => {
                console.log('Cart icon clicked');
                const modal = new bootstrap.Modal(document.getElementById('cartModal'), {
                    keyboard: true // Allow closing with ESC key
                });
                modal.show();
            });
        } else {
            console.warn('Cart icon not found');
        }

        // Fix scroll lock after modal close
        const cartModal = document.getElementById('cartModal');
        if (cartModal) {
            cartModal.addEventListener('hidden.bs.modal', () => {
                console.log('Cart modal closed');
                document.body.classList.remove('modal-open');
                document.body.style.overflow = 'auto';
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());
            });
        } else {
            console.warn('Cart modal not found');
        }
    } catch (error) {
        console.error('Initialization error:', error);
    }
});