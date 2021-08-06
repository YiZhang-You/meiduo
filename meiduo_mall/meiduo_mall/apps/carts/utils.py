import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    """购物车合并，cookies合并到redis"""
    cart_str = request.COOKIES.get('cart')
    if cart_str is None:
        return
    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
    redis_conn = get_redis_connection('cart')
    pl = redis_conn.pipeline()
    for sku_id in cart_dict:
        pl.hset('cart_%d' % user.id, sku_id, cart_dict[sku_id]['count'])
        if cart_dict[sku_id]['selected']:
            pl.sadd('selected_%d' % user.id, sku_id)
    pl.execute()
    response.delete_cookie('cart')
