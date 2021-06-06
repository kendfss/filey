import os, sys, time

user_scripts = r'e:\projects\monties'
shortcuts = {
    'music': os.path.join(os.path.expanduser('~'), 'music', 'collection'),
    'images': os.path.join(os.path.expanduser('~'), 'pictures'),
    'pictures': os.path.join(os.path.expanduser('~'), 'pictures'),
    'pics': os.path.join(os.path.expanduser('~'), 'pictures'),
    'videos': os.path.join(os.path.expanduser('~'), 'videos'),
    'ytdls': {
        'music': {
            'singles': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'music', 'singles'),
            'mixes': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'music', 'mixes'),
            'albums': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'music', 'album'),
        },
        'graff': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'graff'),
        'bullshit': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'bullshitters'),
        'bull': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'bullshitters'),
        'code': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'cscode'),
        'cs': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'cscode'),
        'maths': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'maths'),
        'math': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'maths'),
        'movies': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'movies'),
        'other': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'other'),
        'physics': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'physics'),
        'phys': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'physics'),
        'politics': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'politics'),
        'pol': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'politics'),
    },
    'documents': os.path.join(os.path.expanduser('~'), 'documents'),
    'docs': os.path.join(os.path.expanduser('~'), 'documents'),
    'downloads': os.path.join(os.path.expanduser('~'), 'downloads'),
    'desktop': os.path.join(os.path.expanduser('~'), 'desktop'),
    'books': os.path.join(os.path.expanduser('~'), 'documents', 'bookes'),
    'monties': os.path.join(user_scripts, str(time.localtime()[0])),
    'scripts': user_scripts,
    'demos': os.path.join(user_scripts, 'demos'),
    'site': os.path.join(sys.exec_prefix, 'lib', 'site-packages'),
    'home': os.path.expanduser('~'),
    'user': os.path.expanduser('~'),
    'root': os.path.expanduser('~'),
    '~': os.path.expanduser('~'),
}
os.makedirs(shortcuts['monties'], exist_ok=True)