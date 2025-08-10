// script.js

const BASE_URL = 'http://localhost:5000'; // Adjust if your Flask app runs on a different port/host
const APP_CONTENT_DIV = document.getElementById('app-content');
const CART_ITEM_COUNT_SPAN = document.getElementById('cart-item-count');
const CURRENT_USER_ID_SPAN = document.getElementById('current-user-id');
const USER_ID_DISPLAY_DIV = document.getElementById('user-id-display');
const SEARCH_INPUT = document.getElementById('search-input');

let currentUserId = localStorage.getItem('campusBitesUserId') || generateUniqueId();
let foodItems = [];
let cartItems = [];
let orders = [];
let selectedFoodItem = null;
let currentSearchTerm = '';

// Modals and their elements
const orderReviewModal = document.getElementById('order-review-modal');
const closeOrderReviewModalBtn = document.getElementById('close-order-review-modal');
const reviewFoodNameSpan = document.getElementById('review-food-name');
const reviewFoodPriceSpan = document.getElementById('review-food-price');
const reviewQuantitySpan = document.getElementById('review-quantity');
const reviewQuantityMinusBtn = document.getElementById('review-quantity-minus');
const reviewQuantityPlusBtn = document.getElementById('review-quantity-plus');
const reviewTotalPriceSpan = document.getElementById('review-total-price');
const confirmOrderButton = document.getElementById('confirm-order-button');
const cancelReviewOrderBtn = document.getElementById('cancel-review-order');

const recommendationModal = document.getElementById('recommendation-modal');
const closeRecommendationModalBtn = document.getElementById('close-recommendation-modal');
const recommendationLoading = document.getElementById('recommendation-loading');
const recommendationList = document.getElementById('recommendation-list');
const closeRecommendationButton = document.getElementById('close-recommendation-button');

let itemToReview = null; // Holds { foodItem, quantity } for the order review modal

// --- Utility Functions ---

function generateUniqueId() {
    const id = 'user-' + Math.random().toString(36).substr(2, 9) + Date.now();
    localStorage.setItem('campusBitesUserId', id);
    return id;
}

function getFoodItemDetails(foodId) {
    return foodItems.find(item => item.id === foodId);
}

function updateCartItemCount() {
    const totalCount = cartItems.reduce((acc, item) => acc + item.quantity, 0);
    CART_ITEM_COUNT_SPAN.textContent = totalCount;
    if (totalCount > 0) {
        CART_ITEM_COUNT_SPAN.classList.remove('hidden');
    } else {
        CART_ITEM_COUNT_SPAN.classList.add('hidden');
    }
}

function showModal(modalElement) {
    modalElement.classList.remove('hidden');
    // Re-render Lucide icons if any were added dynamically within the modal
    lucide.createIcons();
}

function hideModal(modalElement) {
    modalElement.classList.add('hidden');
}

// --- API Calls ---

async function fetchData(endpoint, method = 'GET', body = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching from ${endpoint}:`, error);
        // Display user-friendly error message
        APP_CONTENT_DIV.innerHTML = `<div class="container mx-auto p-4 text-center text-red-600">
            <p class="text-lg">Error: ${error.message}. Please try again later.</p>
            <p>Ensure the backend server is running and accessible.</p>
        </div>`;
        throw error; // Re-throw to propagate the error
    }
}

async function fetchFoodItems() {
    foodItems = await fetchData('/api/food_items');
    renderPage('home'); // Re-render current page after fetching
}

async function fetchCartItems() {
    cartItems = await fetchData(`/api/cart/${currentUserId}`);
    updateCartItemCount();
    renderPage('cart'); // Re-render current page after fetching
}

async function fetchOrders() {
    orders = await fetchData(`/api/orders/${currentUserId}`);
    renderPage('orders'); // Re-render current page after fetching
}

async function createUserIfNotExists() {
    try {
        await fetchData('/api/users', 'POST', { userId: currentUserId });
        console.log('User registered with backend:', currentUserId);
    } catch (error) {
        console.error('Failed to register user with backend:', error);
    }
}

// --- Rendering Functions ---

function renderPage(pageName) {
    APP_CONTENT_DIV.innerHTML = ''; // Clear previous content
    let content = '';

    switch (pageName) {
        case 'home':
            content = renderHomePage(foodItems, currentSearchTerm);
            break;
        case 'food-detail':
            content = renderFoodDetail(selectedFoodItem);
            break;
        case 'cart':
            content = renderCartPage(cartItems, foodItems);
            break;
        case 'orders':
            content = renderOrdersPage(orders, foodItems);
            break;
        case 'settings':
            content = renderSettingsPage();
            break;
        default:
            content = `<div class="container mx-auto p-4 text-center text-gray-600">
                <p class="text-lg">Page not found.</p>
            </div>`;
    }
    APP_CONTENT_DIV.innerHTML = content;
    // Re-render Lucide icons after new content is added to the DOM
    lucide.createIcons();
    attachEventListeners(pageName);
}

function renderHomePage(items, searchTerm) {
    const filteredItems = items.filter(item =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return `
        <div class="container mx-auto p-4">
            <h2 class="text-3xl font-bold text-gray-800 mb-6 text-center">Our Delicious Menu</h2>
            ${filteredItems.length === 0 ? `
                <p class="text-center text-gray-600 text-lg">No food items found matching your search.</p>
            ` : `
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                    ${filteredItems.map(item => `
                        <div
                            class="food-item-card bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden transform hover:-translate-y-1"
                            data-food-id="${item.id}"
                        >
                            <img
                                src="${item.image_url}"
                                alt="${item.name}"
                                class="w-full h-48 object-cover rounded-t-xl"
                                onerror="this.onerror=null; this.src='https://placehold.co/400x200/e2e8f0/64748b?text=${encodeURIComponent(item.name)}';"
                            />
                            <div class="p-4">
                                <h3 class="text-xl font-semibold text-gray-900 mb-2">${item.name}</h3>
                                <p class="text-gray-600 text-sm mb-3 line-clamp-2">${item.description}</p>
                                <p class="text-green-700 font-bold text-lg">₹${item.price.toFixed(2)}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `}
        </div>
    `;
}

function renderFoodDetail(foodItem) {
    if (!foodItem) {
        return `
            <div class="container mx-auto p-4 text-center text-gray-600">
                <p>No food item selected. Please go back to the <button id="back-to-home-btn" class="text-blue-600 hover:underline">Home Page</button>.</p>
            </div>
        `;
    }

    return `
        <div class="container mx-auto p-4 flex flex-col md:flex-row items-start md:items-center gap-8 bg-white rounded-xl shadow-lg mt-8">
            <div class="md:w-1/2 w-full">
                <img
                    src="${foodItem.image_url}"
                    alt="${foodItem.name}"
                    class="w-full h-64 md:h-96 object-cover rounded-lg shadow-md"
                    onerror="this.onerror=null; this.src='https://placehold.co/600x400/e2e8f0/64748b?text=${encodeURIComponent(foodItem.name)}';"
                />
            </div>
            <div class="md:w-1/2 w-full p-4">
                <h2 class="text-4xl font-bold text-gray-900 mb-4">${foodItem.name}</h2>
                <p class="text-gray-700 text-lg mb-6 leading-relaxed">${foodItem.description}</p>
                <p class="text-green-700 font-extrabold text-3xl mb-6">₹${foodItem.price.toFixed(2)}</p>

                <div class="flex items-center space-x-4 mb-6">
                    <span class="text-gray-800 text-lg font-semibold">Quantity:</span>
                    <div class="flex items-center border border-gray-300 rounded-lg overflow-hidden">
                        <button id="detail-quantity-minus" class="p-2 bg-gray-100 hover:bg-gray-200 transition duration-200">
                            <i data-lucide="minus" size="20" class="text-gray-600"></i>
                        </button>
                        <span id="detail-quantity" class="px-4 py-2 text-lg font-semibold text-gray-800">1</span>
                        <button id="detail-quantity-plus" class="p-2 bg-gray-100 hover:bg-gray-200 transition duration-200">
                            <i data-lucide="plus" size="20" class="text-gray-600"></i>
                        </button>
                    </div>
                </div>

                <p class="text-red-600 font-medium mb-6">Order Time Limit: Order by 10:00 AM for Breakfast, 2:00 PM for Lunch</p>

                <div class="flex flex-col sm:flex-row gap-4 mb-6">
                    <button id="add-to-cart-btn" class="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg text-lg font-semibold hover:bg-blue-700 transition duration-300 shadow-md flex items-center justify-center space-x-2">
                        <i data-lucide="shopping-cart" size="20"></i>
                        <span>Add to Cart</span>
                    </button>
                    <button id="order-now-btn" class="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg text-lg font-semibold hover:bg-green-700 transition duration-300 shadow-md flex items-center justify-center space-x-2">
                        <i data-lucide="check-circle-2" size="20"></i>
                        <span>Order Now</span>
                    </button>
                </div>
                <button id="get-recommendations-btn" class="w-full bg-purple-600 text-white py-3 px-6 rounded-lg text-lg font-semibold hover:bg-purple-700 transition duration-300 shadow-md flex items-center justify-center space-x-2 mb-4">
                    <i data-lucide="sparkles" size="20"></i>
                    <span>Get Recommendations</span>
                </button>
                <button id="go-to-cart-btn" class="w-full bg-gray-200 text-gray-800 py-3 px-6 rounded-lg text-lg font-semibold hover:bg-gray-300 transition duration-300 shadow-sm flex items-center justify-center space-x-2">
                    <i data-lucide="shopping-cart" size="20"></i>
                    <span>Go to Cart</span>
                </button>
            </div>
        </div>
    `;
}

function renderCartPage(items, allFoodItems) {
    const selectedItems = items.filter(item => item.selected);
    const totalSelectedPrice = selectedItems.reduce((acc, cartItem) => {
        const food = allFoodItems.find(f => f.id === cartItem.food_item_id);
        return acc + (food ? food.price * cartItem.quantity : 0);
    }, 0).toFixed(2);

    return `
        <div class="container mx-auto p-4">
            <h2 class="text-3xl font-bold text-gray-800 mb-6 text-center">Your Cart</h2>
            ${items.length === 0 ? `
                <div class="text-center text-gray-600 text-lg">
                    <p class="mb-4">Your cart is empty.</p>
                    <button id="start-shopping-btn" class="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-300">
                        Start Shopping
                    </button>
                </div>
            ` : `
                <div class="bg-white rounded-xl shadow-lg p-6">
                    ${items.map(cartItem => {
                        const food = allFoodItems.find(f => f.id === cartItem.food_item_id);
                        if (!food) return ''; // Should not happen if data is consistent

                        return `
                            <div class="flex items-center justify-between border-b border-gray-200 py-4 last:border-b-0 cart-item" data-cart-id="${cartItem.id}" data-food-id="${food.id}">
                                <div class="flex items-center space-x-4 flex-grow">
                                    <input
                                        type="checkbox"
                                        class="form-checkbox cart-item-checkbox"
                                        ${cartItem.selected ? 'checked' : ''}
                                    />
                                    <img
                                        src="${food.image_url}"
                                        alt="${food.name}"
                                        class="w-20 h-20 object-cover rounded-lg shadow-sm"
                                        onerror="this.onerror=null; this.src='https://placehold.co/80x80/e2e8f0/64748b?text=${encodeURIComponent(food.name)}';"
                                    />
                                    <div class="flex-grow">
                                        <h3 class="text-xl font-semibold text-gray-900">${food.name}</h3>
                                        <p class="text-gray-600">₹${food.price.toFixed(2)}</p>
                                    </div>
                                </div>
                                <div class="flex items-center space-x-3">
                                    <button
                                        class="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition duration-200 cart-quantity-minus"
                                        ${cartItem.quantity <= 1 ? 'disabled' : ''}
                                    >
                                        <i data-lucide="minus" size="18" class="text-gray-600"></i>
                                    </button>
                                    <span class="text-lg font-semibold text-gray-800 cart-quantity">${cartItem.quantity}</span>
                                    <button
                                        class="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition duration-200 cart-quantity-plus"
                                    >
                                        <i data-lucide="plus" size="18" class="text-gray-600"></i>
                                    </button>
                                </div>
                                <div class="ml-6 text-lg font-bold text-green-700 w-24 text-right">
                                    ₹${(food.price * cartItem.quantity).toFixed(2)}
                                </div>
                            </div>
                        `;
                    }).join('')}
                    <div class="mt-6 pt-4 border-t border-gray-200 flex justify-between items-center">
                        <span class="text-xl font-bold text-gray-800">Total Selected:</span>
                        <span class="text-3xl font-extrabold text-green-700">₹${totalSelectedPrice}</span>
                    </div>
                    <button id="order-selected-items-btn"
                        class="w-full mt-6 bg-green-600 text-white py-3 px-6 rounded-lg text-xl font-semibold hover:bg-green-700 transition duration-300 shadow-md ${selectedItems.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}"
                        ${selectedItems.length === 0 ? 'disabled' : ''}
                    >
                        Order Selected Items (${selectedItems.length})
                    </button>
                </div>
            `}
        </div>
    `;
}

function renderOrdersPage(items, allFoodItems) {
    // Sort orders by order_time in descending order (latest first)
    const sortedOrders = [...items].sort((a, b) => b.order_time - a.order_time);

    return `
        <div class="container mx-auto p-4">
            <h2 class="text-3xl font-bold text-gray-800 mb-6 text-center">Your Orders</h2>
            ${sortedOrders.length === 0 ? `
                <p class="text-center text-gray-600 text-lg">You have no active orders.</p>
            ` : `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    ${sortedOrders.map(order => {
                        const food = allFoodItems.find(f => f.id === order.food_item_id);
                        if (!food) return '';

                        const orderTime = new Date(order.order_time * 1000); // Convert Unix timestamp to Date object
                        const cancelTimeLimit = new Date(orderTime.getTime() + 5 * 60 * 1000); // 5 minutes
                        const canCancel = new Date() < cancelTimeLimit && order.status === 'pending';

                        return `
                            <div class="bg-white rounded-xl shadow-lg p-6 flex flex-col sm:flex-row items-center sm:items-start gap-4">
                                <div class="flex-shrink-0 flex flex-col items-center justify-center p-2 bg-white rounded-lg shadow-inner">
                                    <i data-lucide="qr-code" size="48" class="text-gray-700"></i>
                                    <p class="text-xs text-gray-600 mt-1">Scan for details</p>
                                    <p class="text-xs text-gray-500 break-all text-center">${order.qr_code_data}</p>
                                </div>
                                <div class="flex-grow text-center sm:text-left">
                                    <h3 class="text-2xl font-bold text-gray-900 mb-2">${food.name}</h3>
                                    <p class="text-gray-700 mb-1">Quantity: <span class="font-semibold">${order.quantity}</span></p>
                                    <p class="text-green-700 font-bold text-xl mb-2">Total: ₹${(food.price * order.quantity).toFixed(2)}</p>
                                    <p class="text-gray-600 text-sm">Token: <span class="font-mono font-semibold">${order.token_number}</span></p>
                                    <p class="text-gray-600 text-sm">Ordered At: ${orderTime.toLocaleString()}</p>
                                    <p class="text-gray-600 text-sm mt-2">Status: <span class="font-semibold ${order.status === 'cancelled' ? 'text-red-500' : 'text-blue-500'}">${order.status}</span></p>
                                    ${order.status === 'pending' ? `
                                        <button
                                            class="mt-4 py-2 px-4 rounded-lg font-semibold transition duration-300 order-cancel-btn ${canCancel ? 'bg-red-500 text-white hover:bg-red-600' : 'bg-gray-300 text-gray-600 cursor-not-allowed'}"
                                            data-order-id="${order.id}"
                                            ${!canCancel ? 'disabled' : ''}
                                        >
                                            Cancel Order ${canCancel ? `(before ${cancelTimeLimit.toLocaleTimeString()})` : ''}
                                        </button>
                                    ` : ''}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `}
        </div>
    `;
}

function renderSettingsPage() {
    return `
        <div class="container mx-auto p-4 text-center">
            <h2 class="text-3xl font-bold text-gray-800 mb-6">Settings</h2>
            <p class="text-gray-600 text-lg">Settings options will be available here soon!</p>
            <div class="mt-8 p-6 bg-white rounded-xl shadow-lg inline-block">
                <h3 class="text-xl font-semibold text-gray-800 mb-4">About Campus Bites</h3>
                <p class="text-gray-700 max-w-prose">
                    Campus Bites is your go-to app for convenient food ordering within the college campus.
                    Browse our daily menus for breakfast and lunch, place your orders with ease, and track them
                    in real-time. Enjoy delicious meals without the wait!
                </p>
            </div>
        </div>
    `;
}

// --- Event Listeners and Handlers ---

function attachEventListeners(pageName) {
    // Global Navigation
    document.getElementById('nav-home').onclick = () => renderPage('home');
    document.getElementById('nav-cart').onclick = () => renderPage('cart');
    document.getElementById('nav-orders').onclick = () => renderPage('orders');
    document.getElementById('nav-settings').onclick = () => renderPage('settings');

    // Search functionality
    SEARCH_INPUT.oninput = (e) => {
        currentSearchTerm = e.target.value;
        renderPage('home'); // Re-render home page with filtered results
    };

    // Page-specific event listeners
    if (pageName === 'home') {
        document.querySelectorAll('.food-item-card').forEach(card => {
            card.onclick = () => {
                const foodId = card.dataset.foodId;
                selectedFoodItem = foodItems.find(item => item.id === foodId);
                renderPage('food-detail');
            };
        });
    } else if (pageName === 'food-detail') {
        const detailQuantitySpan = document.getElementById('detail-quantity');
        let quantity = parseInt(detailQuantitySpan.textContent);

        document.getElementById('detail-quantity-minus').onclick = () => {
            quantity = Math.max(1, quantity - 1);
            detailQuantitySpan.textContent = quantity;
        };
        document.getElementById('detail-quantity-plus').onclick = () => {
            quantity++;
            detailQuantitySpan.textContent = quantity;
        };

        document.getElementById('add-to-cart-btn').onclick = async () => {
            await handleAddToCart(selectedFoodItem, quantity);
        };
        document.getElementById('order-now-btn').onclick = () => {
            handleOrderNow(selectedFoodItem, quantity);
        };
        document.getElementById('go-to-cart-btn').onclick = () => renderPage('cart');
        if (document.getElementById('back-to-home-btn')) {
            document.getElementById('back-to-home-btn').onclick = () => renderPage('home');
        }
        document.getElementById('get-recommendations-btn').onclick = async () => {
            await handleGetRecommendations(selectedFoodItem);
        };

    } else if (pageName === 'cart') {
        document.getElementById('order-selected-items-btn').onclick = async () => {
            await handleOrderSelectedItems();
        };
        if (document.getElementById('start-shopping-btn')) {
            document.getElementById('start-shopping-btn').onclick = () => renderPage('home');
        }

        document.querySelectorAll('.cart-item-checkbox').forEach(checkbox => {
            checkbox.onchange = async (e) => {
                const cartId = e.target.closest('.cart-item').dataset.cartId;
                await handleToggleCartItemSelection(cartId, e.target.checked);
            };
        });

        document.querySelectorAll('.cart-quantity-minus').forEach(button => {
            button.onclick = async (e) => {
                const cartItemDiv = e.target.closest('.cart-item');
                const cartId = cartItemDiv.dataset.cartId;
                const currentQuantity = parseInt(cartItemDiv.querySelector('.cart-quantity').textContent);
                await handleUpdateCartQuantity(cartId, currentQuantity - 1);
            };
        });

        document.querySelectorAll('.cart-quantity-plus').forEach(button => {
            button.onclick = async (e) => {
                const cartItemDiv = e.target.closest('.cart-item');
                const cartId = cartItemDiv.dataset.cartId;
                const currentQuantity = parseInt(cartItemDiv.querySelector('.cart-quantity').textContent);
                await handleUpdateCartQuantity(cartId, currentQuantity + 1);
            };
        });

    } else if (pageName === 'orders') {
        document.querySelectorAll('.order-cancel-btn').forEach(button => {
            button.onclick = async (e) => {
                const orderId = e.target.dataset.orderId;
                await handleCancelOrder(orderId);
            };
        });
    }

    // Modal event listeners (attached once)
    closeOrderReviewModalBtn.onclick = () => hideModal(orderReviewModal);
    cancelReviewOrderBtn.onclick = () => hideModal(orderReviewModal);

    reviewQuantityMinusBtn.onclick = () => {
        if (itemToReview) {
            itemToReview.quantity = Math.max(1, itemToReview.quantity - 1);
            reviewQuantitySpan.textContent = itemToReview.quantity;
            reviewTotalPriceSpan.textContent = (itemToReview.foodItem.price * itemToReview.quantity).toFixed(2);
        }
    };
    reviewQuantityPlusBtn.onclick = () => {
        if (itemToReview) {
            itemToReview.quantity++;
            reviewQuantitySpan.textContent = itemToReview.quantity;
            reviewTotalPriceSpan.textContent = (itemToReview.foodItem.price * itemToReview.quantity).toFixed(2);
        }
    };
    confirmOrderButton.onclick = async () => {
        if (itemToReview) {
            await handleConfirmOrder(itemToReview.foodItem, itemToReview.quantity);
        }
    };

    closeRecommendationModalBtn.onclick = () => hideModal(recommendationModal);
    closeRecommendationButton.onclick = () => hideModal(recommendationModal);
}

// --- Core Application Logic ---

async function handleAddToCart(foodItem, quantity) {
    try {
        await fetchData(`/api/cart/${currentUserId}`, 'POST', {
            foodId: foodItem.id,
            quantity: quantity,
            selected: true
        });
        await fetchCartItems(); // Re-fetch cart to update UI
        renderPage('cart'); // Navigate to cart after adding
    } catch (error) {
        console.error("Failed to add to cart:", error);
    }
}

function handleOrderNow(foodItem, quantity) {
    itemToReview = { foodItem, quantity };
    reviewFoodNameSpan.textContent = foodItem.name;
    reviewFoodPriceSpan.textContent = foodItem.price.toFixed(2);
    reviewQuantitySpan.textContent = quantity;
    reviewTotalPriceSpan.textContent = (foodItem.price * quantity).toFixed(2);
    showModal(orderReviewModal);
}

async function handleConfirmOrder(foodItem, quantity) {
    try {
        await fetchData(`/api/orders/${currentUserId}`, 'POST', {
            items: [{ foodId: foodItem.id, quantity: quantity }]
        });
        hideModal(orderReviewModal);
        await fetchOrders(); // Re-fetch orders to update UI
        renderPage('orders'); // Navigate to orders page
    } catch (error) {
        console.error("Failed to confirm order:", error);
    }
}

async function handleUpdateCartQuantity(cartItemId, newQuantity) {
    if (newQuantity < 1) {
        await handleDeleteCartItem(cartItemId);
        return;
    }
    try {
        await fetchData(`/api/cart/${currentUserId}/${cartItemId}`, 'PUT', { quantity: newQuantity });
        await fetchCartItems(); // Re-fetch cart to update UI
    } catch (error) {
        console.error("Failed to update cart quantity:", error);
    }
}

async function handleToggleCartItemSelection(cartItemId, isSelected) {
    try {
        await fetchData(`/api/cart/${currentUserId}/${cartItemId}`, 'PUT', { selected: isSelected });
        await fetchCartItems(); // Re-fetch cart to update UI
    } catch (error) {
        console.error("Failed to toggle cart item selection:", error);
    }
}

async function handleDeleteCartItem(cartItemId) {
    try {
        await fetchData(`/api/cart/${currentUserId}/${cartItemId}`, 'DELETE');
        await fetchCartItems(); // Re-fetch cart to update UI
    } catch (error) {
        console.error("Failed to delete cart item:", error);
    }
}

async function handleOrderSelectedItems() {
    const selectedItems = cartItems.filter(item => item.selected);
    if (selectedItems.length === 0) {
        console.warn("No items selected to order.");
        return;
    }

    const itemsToOrder = selectedItems.map(item => ({
        foodId: item.food_item_id,
        quantity: item.quantity,
        cartItemId: item.id // Pass cart item ID to delete from cart later
    }));

    try {
        await fetchData(`/api/orders/${currentUserId}`, 'POST', { items: itemsToOrder });
        await fetchCartItems(); // Re-fetch cart to update UI (items should be removed)
        await fetchOrders(); // Re-fetch orders to update UI
        renderPage('orders'); // Navigate to orders page
    } catch (error) {
        console.error("Failed to order selected items:", error);
    }
}

async function handleCancelOrder(orderId) {
    try {
        await fetchData(`/api/orders/${currentUserId}/${orderId}`, 'PUT', { status: 'cancelled' });
        await fetchOrders(); // Re-fetch orders to update UI
    } catch (error) {
        console.error("Failed to cancel order:", error);
        // Optionally, display a message to the user about why cancellation failed
    }
}

async function handleGetRecommendations(foodItem) {
    showModal(recommendationModal);
    recommendationLoading.classList.remove('hidden');
    recommendationList.classList.add('hidden');
    recommendationList.innerHTML = ''; // Clear previous recommendations

    try {
        const response = await fetchData('/api/recommendations', 'POST', {
            foodItemName: foodItem.name
        });
        const recommendations = response.recommendations;

        recommendationLoading.classList.add('hidden');
        if (recommendations && recommendations.length > 0) {
            recommendationList.classList.remove('hidden');
            recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                recommendationList.appendChild(li);
            });
        } else {
            recommendationList.classList.remove('hidden');
            recommendationList.innerHTML = '<li>No specific recommendations found at this time.</li>';
        }
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        recommendationLoading.classList.add('hidden');
        recommendationList.classList.remove('hidden');
        recommendationList.innerHTML = `<li class="text-red-500">Could not load recommendations. ${error.message}</li>`;
    }
}

// --- Initialization ---

async function initApp() {
    CURRENT_USER_ID_SPAN.textContent = currentUserId;
    USER_ID_DISPLAY_DIV.classList.remove('hidden'); // Show user ID

    // Ensure user exists in backend DB
    await createUserIfNotExists();

    // Fetch initial data
    await fetchFoodItems();
    await fetchCartItems();
    await fetchOrders();

    // Render initial page (Home)
    renderPage('home');
}

// Run initialization when the DOM is fully loaded
window.onload = initApp;
