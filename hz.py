import flet as ft
import flet_audio as fa
import os
import time
import random
import yt_dlp
import threading

import json
from dialogs import *
from youtube_api import YouTubeDataAPI

#фуфелшмерц краш
#удаление через gu

#плейлисты
# загрузка через исполнитель+песня
#интеграция плейлистов спотифая
#редактирование файла через gu
#псхалка на тройное нажатие обновления

yt = YouTubeDataAPI('AIzaSyC-ZQhsOfHUFz1HjxjuBunPGZ8e8dnHaWk')
if not os.path.isdir('songs'):os.makedirs('songs')
lock = threading.Lock()
def main(page: ft.Page):
    page.title = "СПОТИФАЕИНАТОР 3000"
    current_song = None
    current_vol=20
    is_playing=False
    dur_bar=ft.Slider(min=0, max=1, height=10,on_change_end=lambda e:dur_slider_change_end(e) if current_song else None)
    song_title=ft.Text(size=25,text_align=ft.MainAxisAlignment.CENTER,value='No active song')


    def state_change(e):
        if e.data=='completed' and e.control in page.overlay: next_song(songs)
  
    songs=[fa.Audio(src=f'l:/pr/mp3/songs/{song}',autoplay=False,volume=current_vol/100,on_state_changed=state_change,data=i) for i,song in enumerate(os.listdir('songs'))]
    for song in songs:page.overlay.append(song)
    lv=ft.ListView(width=400,height=400,expand=True)
    
    
    #page.vertical_alignment=ft.MainAxisAlignment.CENTER
    #FUNC \/    

    def update_playlist():
        nonlocal lv
        nonlocal songs
        for song in songs:
            name=song.src.split('/')[-1]
            lv.controls.append(ft.ListTile(
                                            title=ft.Text(song.src.split('/')[-1][:-4]),
                                            on_click=lambda e,t=song:play_song(t),
                                            title_alignment=ft.MainAxisAlignment.CENTER,
                                            trailing=ft.Row([ft.IconButton(
                                                            icon=ft.Icons.EDIT,
                                                            on_click=lambda e,name=song.src.split('/')[-1]: edit_song_dlg(page=page,songfile_name=name)
                                                        ),ft.IconButton(
                                                            icon=ft.Icons.DELETE,
                                                            on_click=lambda e,name=song.src.split('/')[-1]:dlg_delete(page,songfile_name=name)
                                                        )],alignment=ft.MainAxisAlignment.END,wrap=True),

                                )   )

    def passive_update_dur_slider():
        nonlocal current_song,is_playing
        while True:
            if current_song:
                time.sleep(1)
                if 1000*int(is_playing)+dur_bar.value<=dur_bar.max:
                    dur_bar.value+=1000*int(is_playing)
                    page.update()

    def dur_slider_change_end(e):
        current_song.seek(int(e.control.value))
        #volume_slider.visible=False

    def change_vol(e):
        nonlocal current_vol
        current_vol=e.control.value/100
        current_song.volume=current_vol
        page.update()

        volume_slider.visible=True
    
    def update_songs(e=None):
        nonlocal songs
        page.overlay.clear()
        songs=[fa.Audio(src=f'l:/pr/mp3/songs/{song}',autoplay=False,volume=current_vol,on_state_changed=state_change,data=i) for i,song in enumerate(os.listdir('songs'))]
        for song in songs:page.overlay.append(song)
        update_playlist_display(songs)
        
    def next_song(playlist):
        nonlocal current_song
        current_song.pause()
        num=current_song.data
        if num+1<len(playlist):
            play_song(playlist[num+1])  
        else:
           play_song(playlist[0])

    def play_random(playlist):
        nonlocal current_song
        if current_song:current_song.pause()
        #shuffle(playlist=playlist)
        play_song(playlist[random.randint(0,len(playlist)-1)])

    def play_song(song):
        nonlocal current_song,dur_bar,song_title,is_playing
        if current_song in page.overlay: current_song.pause()
        current_song=song
        if current_song not in page.overlay:return
        if current_song: current_song.pause()
        is_playing=True
        current_song.volume = current_vol
        current_song.play()
        song_title.value='Now playing: '+current_song.src.split('/')[-1][:-4]
        
        dur_bar.max=song.get_duration()
        dur_bar.value=0
        page.bottom_appbar.content=ft.Column([dur_bar,song_title])
        #create_dur_bar(song)
        #page.update()

    def stop(e):
        nonlocal current_song,is_playing
        if current_song:
            current_song.pause()
            is_playing=False

    def resume(e):
        nonlocal current_song,is_playing
        if current_song: 
            current_song.resume()
            is_playing=True
    
    def shuffle(playlist=None):
        random.shuffle(playlist)
        res=[song for song in playlist]
        for i,song in enumerate(res):
            song.data=i
        nonlocal songs
        songs=res
        update_playlist_display(playlist)
    
    def update_playlist_display(playlist):
        lv.controls.clear()
        nonlocal songs
        update_playlist()
        page.update()

    page.run_thread(passive_update_dur_slider)
    #FUNC   /\
    #GUI    \/

    volume_slider=ft.Slider(
        min=0,max=100,value=current_vol,
        on_change=change_vol
        )
    
    page.bottom_appbar=ft.BottomAppBar(
        content=ft.Column([dur_bar, song_title]),                        
    )

    download_song_button=ft.ElevatedButton(text='Download',on_click=lambda _:dlg_download(page=page))
    shuffle_button=ft.IconButton(icon=ft.Icons.CHAIR,on_click=lambda _:shuffle(playlist=songs),data=[i for i in songs])
    
    update_playlist()
    page.add(
        ft.Row(#верхние кнопки
            [   
                ft.IconButton(icon=ft.Icons.PAUSE,on_click=stop),
                ft.ElevatedButton(text='Play random',on_click=lambda _:play_random(songs)),
                ft.IconButton(icon=ft.Icons.ARROW_RIGHT,on_click=resume),
                ft.IconButton(icon=ft.Icons.DOUBLE_ARROW,on_click=lambda _:next_song(songs)),
                shuffle_button,
                ],
        alignment=ft.MainAxisAlignment.CENTER),

        ft.Column([ #меню скачки
                    #link_field,
                    download_song_button
                    ],
        alignment=ft.MainAxisAlignment.END),

        ft.Row(
                [ft.Column(
                    [
                        ft.Row([ft.Container(content=lv),   #плейлист и его обновление
                                ft.IconButton(ft.Icons.REPEAT,on_click=update_songs)
                                ],expand=True),
                        ft.Row(
                            [   ft.IconButton(icon=ft.Icons.VOLUME_UP),#громкость
                                volume_slider
                            ],spacing=0,expand=True
                            )
                         ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=0,expand=True
                            )

                    ],expand=True
                )
    )
ft.app(main,view=ft.AppView.FLET_APP_WEB)
