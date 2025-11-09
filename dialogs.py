import flet as ft
import flet_audio as fa
import json
import yt_dlp
import threading
import eyed3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, TCON, APIC
from youtube_api import YouTubeDataAPI
import os
import shutil
import time


yt_options={}
with open('yt_dlp_config.json', 'r', encoding='utf-8') as f:
    yt_options= json.load(f)
yt = YouTubeDataAPI('AIzaSyC-ZQhsOfHUFz1HjxjuBunPGZ8e8dnHaWk')
ydl = yt_dlp.YoutubeDL(yt_options)


def edit_song_dlg(page:ft.Page,song:fa.Audio):
    page.overlay.remove(song)
    
    name=song.src.split('/')[-1][:-4]
    path=song.src
    try:
        tags=ID3(path)
        tags.delete()
    except: pass
    old_album=str(tags['TALB'])
    old_artist=str(tags['TPE1'])

    album_field=ft.TextField(label='album',value=old_album)
    name_field=ft.TextField(label='name',value=name)
    artist_field=ft.TextField(label='artist',value=old_artist)
    
    
   
    def edit_song(e):
        new_name=name_field.value
        
        if artist_field.value: tags.add(TPE1(encoding=3, text=artist_field.value))
        if album_field.value: tags.add(TALB(encoding=3, text=album_field.value))
        tags.save(path)
        if new_name!= name: os.rename(path, f'songs/{new_name}.mp3')
        
        page.overlay.append(song)
        page.update()
        page.close(dlg)
        

    confirm_button=ft.TextButton(text='Confirm',on_click=edit_song)
    dlg=ft.AlertDialog(
        modal=True,
        title=f'Edit metadata {name}',
        content=ft.Column([
            name_field,artist_field,album_field,
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