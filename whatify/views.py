from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.utils.http import urlquote

from WhatManager2.utils import json_return_method, get_artists_list
from home import info_holder
from home.models import WhatTorrent, get_what_client, TransTorrent
from player.player_utils import get_playlist_files, get_metadata_dict
from what_meta.models import WhatTorrentGroup, WhatArtist, WhatMetaFulltext
from what_transcode.utils import html_unescape


def index(request):
    return render(request, 'whatify/index.html')


def get_torrent_group_dict(torrent_group):
    return {
        'id': torrent_group.id,
        'joined_artists': torrent_group.joined_artists,
        'artists': get_artists_list(torrent_group.info),
        'name': torrent_group.name,
        'wiki_image': torrent_group.wiki_image,
        'wiki_body': torrent_group.wiki_body,
    }


@json_return_method
def search(request, query):
    meta_fulltext = WhatMetaFulltext.objects.only('id', 'artist', 'torrent_group')
    meta_fulltext = meta_fulltext.extra(
        where=['MATCH(`info`, `more_info`) AGAINST (%s IN BOOLEAN MODE)'], params=[query])
    meta_fulltext = meta_fulltext.extra(select={'score': 'MATCH (`info`) AGAINST (%s)'},
                                        select_params=[query])
    meta_fulltext = meta_fulltext.extra(order_by=['-score'])
    meta_fulltext = meta_fulltext.prefetch_related('artist', 'torrent_group')
    results = []
    for result in meta_fulltext:
        if result.artist:
            results.append({'type': 'artist', 'artist': get_artist_dict(result.artist)})
        elif result.torrent_group:
            results.append({
                'type': 'torrent_group',
                'torrent_group': get_torrent_group_dict(result.torrent_group)
            })
    return results


@json_return_method
def get_torrent_group(request, group_id):
    try:
        torrent_group = WhatTorrentGroup.objects.get(id=group_id)
    except WhatTorrentGroup.DoesNotExist:
        what_client = get_what_client(request)
        torrent_group = WhatTorrentGroup.update_from_what(what_client, group_id)
    torrents = WhatTorrent.objects.filter(torrent_group=torrent_group)
    torrent = None
    for candidate in torrents:
        if candidate.info_format == 'MP3':
            torrent = candidate
    if torrent is None:
        for candidate in torrents:
            torrent = candidate
    data = get_torrent_group_dict(torrent_group)
    if torrent and torrent.master_trans_torrent is not None:
        data.update({
            'playlist': [
                {
                    'id': 'what/' + str(torrent.id) + '#' + str(i),
                    'url': reverse('player.views.get_file') + '?path=' + urlquote(path),
                    'metadata': get_metadata_dict(path)
                }
                for i, path in enumerate(get_playlist_files('what/' + str(torrent.id))[1])
            ]
        })
    return data


def get_artist_dict(artist, include_torrents=False):
    data = {
        'id': artist.id,
        'name': artist.name,
        'image': artist.image,
        'wiki': artist.wiki_body,
    }
    if include_torrents:
        assert not artist.is_shell, 'Can not get torrents for a shell artist'
        group_ids = [t['groupId'] for t in artist.info['torrentgroup']]
        torrent_ids = WhatTorrent.objects.filter(
            torrent_group_id__in=group_ids).values_list('id', flat=True)
        torrents_done = {
            t.what_torrent_id: t.torrent_done for t in
            TransTorrent.objects.filter(what_torrent_id__in=torrent_ids)
        }

        def get_artist_group_dict(torrent_group):
            have = False
            for torrent in torrent_group['torrent']:
                if torrent['id'] in torrents_done:
                    done = torrents_done[torrent['id']]
                    if done == 1:
                        have = True
                    elif have is not True:
                        have = max(have, done)
            return {
                'id': torrent_group['groupId'],
                'name': html_unescape(torrent_group['groupName']),
                'year': torrent_group['groupYear'],
                'have': have,
            }

        data.update({
            'torrentGroups': {
                releaseTypeName: [
                    get_artist_group_dict(t)
                    for t in sorted(artist.info['torrentgroup'], key=lambda g: g['groupYear'])
                    if t['releaseType'] == releaseTypeId
                ]
                for releaseTypeId, releaseTypeName in info_holder.WHAT_RELEASE_TYPES
            } if not artist.is_shell else None,
        })
    return data


@json_return_method
def get_artist(request, artist_id):
    artist = WhatArtist.objects.get(id=artist_id)
    if artist.is_shell:
        artist.update_from_what(get_what_client(request))
    return get_artist_dict(artist, True)
