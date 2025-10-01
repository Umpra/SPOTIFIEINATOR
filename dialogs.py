import flet as ft
import flet_audio as fa
import json
import yt_dlp
import threading
import eyed3
from youtube_api import YouTubeDataAPI
import os

def load_yt_dlp_config():
        config={}
        with open('yt_dlp_config.json', 'r', encoding='utf-8') as f:
            config= json.load(f)
        return config
yt = YouTubeDataAPI('AIzaSyC-ZQhsOfHUFz1HjxjuBunPGZ8e8dnHaWk')
yt_options=load_yt_dlp_config()
ydl = yt_dlp.YoutubeDL(yt_options)


def edit_song_dlg(page,songfile_name):
    eyed3file=eyed3.load(f'songs/{songfile_name}')
    album_field=ft.TextField(label='album',value=eyed3file.tag.album)
    name_field=ft.TextField(label='name',value=songfile_name[:-4])
    artist_field=ft.TextField(label='artist',value=eyed3file.tag.artist)

    def edit_song(path,file,album=None,name=None,artist=None):
        print('EDIT song func:'+path)
        #file=eyed3.load(path)
        file.tag.album=album
        file.tag.artist=artist
        file.tag.save()
        if name!=path.split('/')[-1][:-4]:
            print('name changed')
            os.rename(path,f'{'/'.join(path.split('/')[:-1])}/{name}.mp3')

    confirm_button=ft.TextButton(text='Confirm',on_click=lambda e: 
                                 edit_song(path=f'songs/{songfile_name}', file=eyed3file,name=name_field.value,album=album_field.value,artist=artist_field.value))
    dlg=ft.AlertDialog(
        title=f'Edit metadata {songfile_name[:-4]}',
        content=ft.Column([
            name_field,artist_field,album_field
        ]),
        actions=[confirm_button]
    )
    page.open(dlg)

def dlg_download(page):
    link_field=ft.TextField(label='youtube link')
    artist_field=ft.TextField(label='artist')
    name_field=ft.TextField(label='name')

    dlg_playlist_confirm=ft.AlertDialog(
        title=ft.Text('Are you sure?'),
        content=ft.Text('This a PLAYLIST not a song'),
        actions=[
            ft.ElevatedButton(text='Yes',on_click=lambda _:(page.close(dlg_playlist_confirm),
                                                            ydl.download(link_field.value)
                                                            )),
            ft.ElevatedButton(text='Download only song',on_click=lambda _:
                                                    (page.close(dlg_playlist_confirm),
                                                     ydl.download(link_field.value.split('&')[0]))),
            ft.ElevatedButton(text='Cancel',on_click=lambda _: page.close(dlg_playlist_confirm))
        ]   
    )

    def download_song(url=None, artist=None,song_name=None):
        if url:
            if '&list' not in url:ydl.download(url)
            else: page.open(dlg_playlist_confirm)
        if song_name:
            search_results=yt.search(q=f'{artist} {song_name}', max_results=1)[0]['video_id']
            print(search_results)
            ydl.download(search_results)
    def start_download(e):
        url=link_field.value
        artist=artist_field.value
        song_name=name_field.value
        thread = threading.Thread(
                target=download_song, 
                args=(url,artist,song_name), 
                daemon=True
            )
        thread.start()
        page.update()
         

    download_from_url_button=ft.ElevatedButton(text='Download from url',on_click=lambda e:start_download(e))
    download_search_button=ft.ElevatedButton(text='Download with search',on_click=lambda e:start_download(e))
    download_song_button=ft.ElevatedButton(text='Download',on_click=lambda _:page.open(dlg_download))

    dlg=ft.AlertDialog(
        actions=[
            ft.Container(
                    ft.Row([
                        ft.Column([
                            link_field,
                            download_from_url_button
                        ]),
                        ft.Column([
                            artist_field,
                            name_field,
                            download_search_button
                        ])
                    ],width=600,vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=25
                )
        ]
    )
    page.open(dlg)

def dlg_delete(page,songfile_name):
    
    def del_song(songfile_name):
        os.remove(f'songs/{songfile_name}'),
        page.close(dlg)

    dlg=ft.AlertDialog(title='Are you want to delete?',
                       actions=[
                           ft.TextButton(text='YES', on_click=lambda e: del_song(songfile_name))
                       ])
    page.open(dlg)