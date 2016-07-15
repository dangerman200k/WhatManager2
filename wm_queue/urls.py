from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'wm_queue.views.index'),
    url(r'^part/queue_stats$', 'wm_queue.parts.queue_stats'),
    url(r'^queue_pop$', 'wm_queue.parts.queue_pop'),
    url(r'^pop_remove', 'wm_queue.parts.pop_remove'),
    url(r'^do_pop$', 'wm_queue.parts.do_pop'),
    url(r'^auto_pop$', 'wm_queue.parts.auto_pop'),
    url(r'^add_artist/(.+)$', 'wm_queue.parts.add_artist'),
    url(r'^add_collage/(\d+)$', 'wm_queue.parts.add_collage'),
)
