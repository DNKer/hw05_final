from django.core.paginator import Paginator


def pagination(posts, request, records: int):
    """Pagination function"""
    paginator = Paginator(posts, records)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
