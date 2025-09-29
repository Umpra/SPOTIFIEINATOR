import flet as ft
import flet_audio as fa
import os
import time
import random
import yt_dlp
import threading
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


    #page.vertical_alignment=ft.MainAxisAlignment.CENTER
    #FUNC \/    
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

    def hide_volume_bar(e):
        volume_slider.visible=False

    def change_vol(e):
        nonlocal current_vol
        current_vol=e.control.value/100
        current_song.volume=current_vol
        page.update()

    def show_volume_bar(e):
        volume_slider.visible=True

    def state_change(e):
        if e.data=='completed' and e.control in page.overlay: next_song(songs)
    
    def download_song(url=None, artist=None,song_name=None):
        if url:
            if '&list' not in url:ydl.download(url)
            else: page.open(dlg_playlist_confirm)
        if song_name:
            search_results=yt.search(q=f'{artist} {song_name}', max_results=1)[0]['video_id']
            ydl.download(search_results)

    def download_button():
        pass

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
        for song in playlist:
            lv.controls.append(ft.ListTile(title=ft.Text(song.src.split('/')[-1][:-4]),
                                       on_click=lambda e,t=song:play_song(t),
                                       title_alignment=ft.MainAxisAlignment.CENTER,
                                       ))
        page.update()

    def on_download_complete(d):
        if d['status']=='finished':
            update_songs()
    
    page.run_thread(passive_update_dur_slider)
    #FUNC   /\
    #GUI    \/
    yt_options={
        'format':'best audio',
        'outtmpl':'songs/%(title)s.mp3',
        'progress_hooks': [on_download_complete],
        }
    ydl = yt_dlp.YoutubeDL(yt_options)

    volume_slider=ft.Slider(
        min=0,max=100,value=current_vol,
        on_change=change_vol
        )
    
    page.bottom_appbar=ft.BottomAppBar(
        content=ft.Column([dur_bar, song_title]),                        
    )

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

    link_field=ft.TextField(label='youtube link')
    artist_field=ft.TextField(label='artist')
    name_field=ft.TextField(label='name')

    download_from_url_button=ft.ElevatedButton(text='Download from url',on_click=lambda _:download_song(url=link_field.value))
    download_search_button=ft.ElevatedButton(text='Download with search',on_click=lambda _:download_song(
    artist=artist_field.value,song_name=name_field.value))
    download_song_button=ft.ElevatedButton(text='Download',on_click=lambda _:page.open(dlg_download))

    dlg_download=ft.AlertDialog(
        modal=True,
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
    songs=[fa.Audio(src=f'l:/pr/mp3/songs/{song}',autoplay=False,volume=current_vol/100,on_state_changed=state_change,data=i) for i,song in enumerate(os.listdir('songs'))]
    for song in songs:page.overlay.append(song)

    lv=ft.ListView(width=400,height=400,expand=True)
    for song in songs:
        lv.controls.append(ft.ListTile(title=ft.Text(song.src.split('/')[-1][:-4]),
                                       on_click=lambda e,t=song:play_song(t),
                                       title_alignment=ft.MainAxisAlignment.CENTER,
                                       ))
        
    shuffle_button=ft.IconButton(icon=ft.Icons.CHAIR,on_click=lambda _:shuffle(playlist=songs),data=[i for i in songs])

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
