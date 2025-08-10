function addToCart(foodId) {
  const qty = document.getElementById('qty').value;
  fetch('/cart/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ food_id: foodId, quantity: qty })
  }).then(res => {
    if (res.ok) alert('Added to cart!');
  });
}

function orderNow(foodId) {
  const qty = document.getElementById('qty').value;
  fetch('/order/now', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ food_id: foodId, quantity: qty })
  }).then(res => {
    if (res.ok) window.location.href = "/orders";
  });
}

function updateQty(cartItemId, action) {
  fetch('/cart/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cart_item_id: cartItemId, action: action })
  }).then(() => location.reload());
}

function removeFromCart(cartItemId) {
  fetch('/cart/remove', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cart_item_id: cartItemId })
  }).then(() => location.reload());
}

function placeOrder() {
  fetch('/order/place-all', {
    method: 'POST'
  }).then(res => {
    if (res.ok) window.location.href = '/orders';
  });
}
