# Test Cases

`Passed (C/F/W)` = passed in Chromium, Firefox and WebKit. Preconditions are "fresh isolated browser
context and healthy SUT" unless stated otherwise.

| ID | Objective | Test data | Preconditions | Expected result | Execution result | Pytest identifier |
|---|---|---|---|---|---|---|
| TC-HOME-001 | Home page loads | – | – | Title contains ShopEase; search field visible | Passed (C/F/W) | `tests/test_catalog.py::test_catalog_loads` |
| TC-HOME-002 | Ten product cards shown | 10 products | – | Exactly 10 cards | Passed (C/F/W) | `tests/test_catalog.py::test_catalog_has_ten_products` |
| TC-HOME-003 | Guest cart starts empty | – | No session | Cart count is 0 | Passed (C/F/W) | `tests/test_catalog.py::test_guest_cart_starts_empty` |
| TC-HOME-004 | Navigation links present | Home, Cart, Login, Register | – | All links visible | Passed (C/F/W) | `tests/test_catalog.py::test_navigation_links_present` |
| TC-HOME-005 | Prices displayed | 10 products | – | Ten `$` prefixed prices | Passed (C/F/W) | `tests/test_catalog.py::test_product_prices_displayed` |
| TC-SEARCH-001 | Search returns match | 3 queries | – | Expected product visible | Passed (C/F/W) | `tests/test_catalog.py::test_search_returns_matching_product` |
| TC-SEARCH-002 | Case-insensitive search | `headphones` | – | Wireless Bluetooth Headphones visible | Passed (C/F/W) | `tests/test_catalog.py::test_search_is_case_insensitive` |
| TC-SEARCH-003 | No results | unknown query | – | Zero cards | Passed (C/F/W) | `tests/test_catalog.py::test_search_no_results` |
| TC-SEARCH-004 | Empty search | empty string | – | All 10 cards | Passed (C/F/W) | `tests/test_catalog.py::test_empty_search_shows_all` |
| TC-CAT-001 | Each category filters | 4 categories | – | Category products shown | Passed (C/F/W) | `tests/test_catalog.py::test_category_filter` |
| TC-CAT-002 | Combined search + filter | Watch / Electronics | – | Exactly Smart Watch | Passed (C/F/W) | `tests/test_catalog.py::test_combined_search_and_filter` |
| TC-CART-001 | Add from catalogue | Mechanical Keyboard | – | Cart total 119.99 | Passed (C/F/W) | `tests/test_cart.py::test_add_single_item` |
| TC-CART-002 | Cart count matches quantity | Smart Watch | – | Count is 1 | Passed (C/F/W) | `tests/test_cart.py::test_cart_count_matches_quantity` |
| TC-CART-003 | Multiple products total | Keyboard + Yoga Mat | – | Total 149.98 | Passed (C/F/W) | `tests/test_cart.py::test_multiple_products_and_total` |
| TC-CART-004 | Update quantity recalculates | qty 2 | Item in cart | Subtotal and total 399.98 | Passed (C/F/W) | `tests/test_cart.py::test_update_quantity_recalculates` |
| TC-CART-005 | Minimum quantity | qty 1 | Item in cart | Total 59.99 | Passed (C/F/W) | `tests/test_cart.py::test_quantity_one_allowed` |
| TC-CART-006 | Remove item | Webcam | Item in cart | Cart empty | Passed (C/F/W) | `tests/test_cart.py::test_remove_item` |
| TC-CART-007 | Empty cart total | – | Fresh context | Total 0.00 | Passed (C/F/W) | `tests/test_cart.py::test_empty_cart_total_is_zero` |
| TC-CART-008 | Repeat add increments qty | Webcam x2 | – | One line, subtotal 119.98 | Passed (C/F/W) | `tests/test_cart.py::test_add_same_product_twice_increments_quantity` |
| TC-CART-009 | Add from catalogue (smoke) | first product | – | Count becomes 1 | Passed (C/F/W) | `tests/test_catalog.py::test_add_to_cart_from_catalog` |
| TC-PROD-001 | All product details | 10 product IDs | – | Correct name and price | Passed (C/F/W) | `tests/test_product_details.py::test_product_details` |
| TC-PROD-002 | Unknown product | ID 99999 | – | 404 page | Passed (C/F/W) | `tests/test_product_details.py::test_invalid_product_returns_404` |
| TC-PROD-003 | Default quantity | product 1 | – | Value is 1 | Passed (C/F/W) | `tests/test_product_details.py::test_default_quantity_is_one` |
| TC-PROD-004 | Add from product page | product 1 | – | One item, subtotal 79.99 | Passed (C/F/W) | `tests/test_product_details.py::test_add_to_cart_from_product_page` |
| TC-PROD-005 | Price consistency | Smart Watch | – | Detail price matches catalogue | Passed (C/F/W) | `tests/test_product_details.py::test_product_page_price_matches_catalog` |
| TC-CO-001 | Successful checkout | Smart Watch | Item in cart | Confirmation with order ID | Passed (C/F/W) | `tests/test_checkout.py::test_successful_checkout` |
| TC-CO-002 | Cart cleared after order | Smart Watch | Item in cart | Cart empty | Passed (C/F/W) | `tests/test_checkout.py::test_checkout_clears_cart` |
| TC-CO-003 | Order in history | Smart Watch | Completed order | Order ID visible | Passed (C/F/W) | `tests/test_checkout.py::test_order_appears_in_history` |
| TC-CO-004 | Order detail opens | Completed order | Order exists | ID present on detail page | Passed (C/F/W) | `tests/test_checkout.py::test_order_detail_opens` |
| TC-CO-005 | Checkout form validation | invalid email | Item in cart | Validation error shown | Passed (C/F/W) | `tests/test_checkout.py::test_checkout_requires_valid_form` |
| TC-CO-006 | Empty cart checkout | – | Fresh context | Redirect away from /checkout | Passed (C/F/W) | `tests/test_checkout.py::test_empty_cart_redirects_from_checkout` |
| TC-CO-007 | History requires login | – | Not logged in | Redirect to /login | Passed (C/F/W) | `tests/test_checkout.py::test_order_history_requires_login` |
| TC-CO-008 | Registered user checkout | ui-tester@example.com | Fresh registration | Order in history | Passed (C/F/W) | `tests/test_checkout.py::test_registered_user_checkout` |
| TC-AUTH-001 | Valid login | demo credentials | – | Logout link visible | Passed (C/F/W) | `tests/test_authentication.py::test_valid_login` |
| TC-AUTH-002 | Invalid email | unknown@example.com | – | Invalid credentials error | Passed (C/F/W) | `tests/test_authentication.py::test_invalid_email` |
| TC-AUTH-003 | Invalid password | WrongPassword123 | – | Invalid credentials error | Passed (C/F/W) | `tests/test_authentication.py::test_invalid_password` |
| TC-AUTH-004 | Empty credentials | empty strings | – | Submission blocked | Passed (C/F/W) | `tests/test_authentication.py::test_empty_credentials_blocked` |
| TC-AUTH-005 | Registration | new-user@example.com | – | Logout link visible | Passed (C/F/W) | `tests/test_authentication.py::test_registration` |
| TC-AUTH-006 | Duplicate email | demo@example.com | – | Already registered error | Passed (C/F/W) | `tests/test_authentication.py::test_duplicate_email_rejected` |
| TC-AUTH-007 | Short password | `abc` | – | Invalid registration data | Passed (C/F/W) | `tests/test_authentication.py::test_short_password_rejected` |
| TC-AUTH-008 | Logout | demo credentials | Logged in | Login link visible | Passed (C/F/W) | `tests/test_authentication.py::test_logout` |
| TC-NEG-001 | Invalid quantities | 0, -1, 11, 999 | – | HTTP 400 with quantity error | Passed (C/F/W) | `tests/test_negative_scenarios.py::test_invalid_quantity_rejected` |
| TC-NEG-002 | Unknown product add | ID 99999 | – | HTTP 404 | Passed (C/F/W) | `tests/test_negative_scenarios.py::test_unknown_product_add_rejected` |
| TC-NEG-003 | Missing product ID | no product_id | – | HTTP 400 | Passed (C/F/W) | `tests/test_negative_scenarios.py::test_missing_product_id_rejected` |
| TC-NEG-004 | Non-numeric product | `abc` | – | HTTP 400 | Passed (C/F/W) | `tests/test_negative_scenarios.py::test_non_numeric_product_rejected` |
| TC-NEG-005 | Unsupported method | GET /cart/add | – | HTTP 405 | Passed (C/F/W) | `tests/test_negative_scenarios.py::test_unsupported_method_rejected` |
| TC-NEG-006 | Unknown API product | ID 99999 | – | HTTP 404 | Passed (C/F/W) | `tests/test_negative_scenarios.py::test_unknown_api_product` |
| TC-NEG-007 | Unknown page | ID 123456 | – | 404 heading | Passed (C/F/W) | `tests/test_negative_scenarios.py::test_unknown_page_shows_404` |
| TC-NEG-008 | Update missing item | ID 99999 | – | HTTP 404 | Passed (C/F/W) | `tests/test_negative_scenarios.py::test_cart_update_missing_item_rejected` |
| TC-ISO-001 | Context B starts empty | two contexts | A adds product | B cart count 0 | Passed (C/F/W) | `tests/test_session_isolation.py::test_context_b_starts_empty` |
| TC-ISO-002 | Orders not shared | two contexts | A places order | B cannot see order ID | Passed (C/F/W) | `tests/test_session_isolation.py::test_context_b_cannot_see_orders` |
| TC-ISO-003 | Checkout isolation | two contexts | Both have carts | B cart intact after A checkout | Passed (C/F/W) | `tests/test_session_isolation.py::test_checkout_does_not_clear_other_cart` |
| TC-ISO-004 | Concurrent checkouts | two contexts | Both have carts | Two distinct order IDs | Passed (C/F/W) | `tests/test_session_isolation.py::test_two_contexts_can_checkout_concurrently` |
