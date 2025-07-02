import flet as ft
import flet_audio as fa
import os
import random
import yt_dlp

current_song = None
current_vol=0.2

#изменение громкости с прогресбарорм
#прогресбар трека
#фуфелшмерц краш
#удаление через gu
#отображение текущего трека
#загрузка через исполнитель+песня
#интеграция плейлистов спотифая
#редактирование файла через gu
#псхалка на тройное нажатие обновления

if not os.path.isdir('songs'):os.makedirs('songs')
def main(page: ft.Page):
    page.title = "СПОТИФАЕИНАТОР 3000"

    #page.vertical_alignment=ft.MainAxisAlignment.CENTER

    #FUNC \/

    def hide_volume_bar(e):
        volume_slider.visible=False
        page.update()
    def change_vol(e):
        global current_vol
        current_vol=e.control.value/100
        current_song.volume=current_vol
        page.update()

    def show_volume_bar(e):
        volume_slider.visible=True
        page.update()

    def state_change(e):
        if e.data=='completed' and e.control in page.overlay: next_song(songs)
    
    def download_song(link=None):
        if not link:link=link_field.value
        if '&list' not in link:ydl.download(link)
        else: page.open(dlg_confirm)

    def update_songs(e=None):
        nonlocal songs
        page.overlay.clear()
        songs=[fa.Audio(src=f'l:/pr/mp3/songs/{song}',autoplay=False,volume=current_vol,on_state_changed=state_change,data=i) for i,song in enumerate(os.listdir('songs'))]
        for song in songs:page.overlay.append(song)
        page.update()
        update_playlist_display(songs)
        

    def next_song(playlist):
        global current_song
        current_song.pause()
        num=current_song.data
        if num+1<len(playlist):
            play_song(playlist[num+1])
            
        else:
            current_song=playlist[0]
            current_song.play()

    def play_random(playlist):
        global current_song
        if current_song:current_song.pause()
        #shuffle(playlist=playlist)
        current_song=playlist[random.randint(0,len(playlist)-1)]
        current_song.play()

    def play_song(song):
        global current_song
        if current_song in page.overlay: current_song.pause()
        current_song=song
        if current_song not in page.overlay:return
        if current_song: current_song.pause()
        current_song.play()
        page.bottom_appbar.content.value='Now playing :'+current_song.src.split('/')[-1][:-4]
        page.update()

    def stop(e):
        global current_song
        if current_song:current_song.pause()

    def resume(e):
        global current_song
        if current_song: current_song.resume()

    def shuffle(playlist=None):
        random.shuffle(playlist)
        res=[song for song in playlist]
        for i,song in enumerate(res):
            song.data=i
        nonlocal songs
        songs=res
        update_playlist_display(playlist)
        page.update()
        print(songs)
    
    
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
    #FUNC   /\
    #GUI    \/
    yt_options={
        'format':'bestaudio',
        'outtmpl':'songs/%(title)s.mp3',
        'progress_hooks': [on_download_complete]
        }
    ydl = yt_dlp.YoutubeDL(yt_options)

    volume_slider=ft.Slider(
        min=0,max=100,value=current_vol,visible=False,
        on_change=change_vol,
        on_change_end=hide_volume_bar
    )

    page.bottom_appbar=ft.BottomAppBar(
        content=ft.Text(size=25,text_align=ft.MainAxisAlignment.CENTER,value='No active song'),                        
    )

    dlg_confirm=ft.AlertDialog(
        title=ft.Text('Are you sure?'),
        content=ft.Text('This a PLAYLIST not a song'),
        actions=[
            ft.ElevatedButton(text='Yes',on_click=lambda _:(page.close(dlg_confirm),
                                                            ydl.download(link_field.value)
                                                            )),
            ft.ElevatedButton(text='Download only song',on_click=lambda _:
                                                    (page.close(dlg_confirm),
                                                     ydl.download(link_field.value.split('&')[0]))),
            ft.ElevatedButton(text='Cancel',on_click=lambda _: page.close(dlg_confirm))
        ]   
    )



    link_field=ft.TextField(label='youtube link',width=400)
    download_button=ft.ElevatedButton(text='Downlaod',on_click=lambda _:download_song())

    songs=[fa.Audio(src=f'l:/pr/mp3/songs/{song}',autoplay=False,volume=current_vol,on_state_changed=state_change,data=i) for i,song in enumerate(os.listdir('songs'))]
    for song in songs:page.overlay.append(song)

    lv=ft.ListView(width=400,height=400)
    for song in songs:
        lv.controls.append(ft.ListTile(title=ft.Text(song.src.split('/')[-1][:-4]),
                                       on_click=lambda e,t=song:play_song(t),
                                       title_alignment=ft.MainAxisAlignment.CENTER,
                                       ))
        
    shuffle_button=ft.IconButton(icon=ft.Icons.CHAIR,on_click=lambda _:shuffle(playlist=songs),data=[i for i in songs])


    page.add(
        ft.Row(
            [
                ft.IconButton(icon=ft.Icons.PAUSE,on_click=stop),
                ft.ElevatedButton(text='Play random',on_click=lambda _:play_random(songs)),
                ft.IconButton(icon=ft.Icons.ARROW_RIGHT,on_click=resume),
                ft.IconButton(icon=ft.Icons.DOUBLE_ARROW,on_click=lambda _:next_song(songs)),
                shuffle_button,
                ],
        alignment=ft.MainAxisAlignment.CENTER),

        ft.Column([
                    link_field,
                    download_button
                    ],
        alignment=ft.MainAxisAlignment.END),

        ft.Row(
                [ft.Column(
                    [
                        ft.Row([ft.Container(content=lv),
                                ft.IconButton(ft.Icons.REPEAT,on_click=update_songs)
                    ]),
                        ft.Row(
                            [
                                ft.IconButton(icon=ft.Icons.VOLUME_UP,on_hover=show_volume_bar),
                                volume_slider
                            ],spacing=0
                            )
                         ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=0,expand=True
                            ),

                    ]
                )

)

ft.app(main,view=ft.AppView.FLET_APP_WEB)
