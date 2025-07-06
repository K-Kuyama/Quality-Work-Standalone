import React, { useState } from 'react';
import Button from 'react-bootstrap/Button';
import Settings from "../Settings";
import Cookies from "universal-cookie";


function AudioActivityTag(props){

    const [app, setApp] = useState(props.data['another_app']);
    const [title, setTitle] = useState(props.data['another_title']);
    const [selected_title, setSelectedTitle] = useState(props.data['selected']);
    const [show_policy, setShowPolicy] = useState(props.data['show_policy']);

    const handleApp = (e) => setApp(e.target.value);
    const handleTitle = (e) => setTitle(e.target.value);

    const setSelect = (d) =>{
        /* どのタイトルを使うかの設定*/
        let s = d.target.value
        console.log(s)
        setSelectedTitle(Number(s))
    }

    const setPolicy = (d) =>{
        setShowPolicy(Number(d.target.value))
    }

    const setSettings = (d) =>{
        /* アプリ名、タイトルをデータベースに保存*/
        console.log("app: "+app)
        console.log("titile: "+title)
        console.log("selected: "+selected_title)
        console.log("show_policy: "+show_policy)

        let additional_str =props.data['id']+"/";
        let method_str = "PATCH";
        let target = Settings.HOME_PATH+'/api/AudioActivity/UpdateActivity/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/AudioActivity/UpdateActivity/'
        }
        let request_body ={another_app: app, another_title: title, 
                            selected: selected_title, show_policy: show_policy};
        let cookies = new Cookies();
        let token = cookies.get('csrftoken')

        fetch(target+additional_str, {
            method : method_str,
            credentials: "same-origin",
            headers: {
                    'Content-Type' : 'application/json',
                    'X-CSRFToken': token,
                },
            body : JSON.stringify(request_body)		
            }
        )
        .then(response => response.json())
        .then(result =>{
            //console.log("perspective set original response ", result);
            const txt = JSON.stringify(result, null,' ');
            //console.log("perspective set text result ", txt);
            let res = JSON.parse(txt);
            console.log("result= ", res);
            //console.log("res id=", res['id']);
            //handleChangePerspective(res['id']);	
        })
        .catch(error =>{
            console.error(error);
        })
    }


    if(props.data){
        return(
            <div className="audio_activity_tag">
                <div className="audio_time_column">
                    <div className="audio_time_labels">
                        <label className="audio_date_title">開始&nbsp;&nbsp;</label><label className="audio_date">{props.data['start_time']}</label>
                    </div>
                    <div className="audio_time_labels">
                        <label className="audio_date_title">終了&nbsp;&nbsp;</label><label className="audio_date">{props.data['end_time']}</label>
                    </div>
                </div>
                <div className="audio_duration">
                    <label className="audio_duration_label">{props.data['duration']}秒</label>
                </div>
                <div className="audio_title_column">
                    <div className="audio_title_label">
                        <label><input type="radio" name={"audio_titles"+props.data['id']} id="id-0" value="0" checked={selected_title === 0} onChange={setSelect} />
                        &nbsp;{props.data['start_app']+":"+props.data['start_title']} </label>
                    </div>
                    <div className="audio_title_label">
                        <label><input type="radio" name={"audio_titles"+props.data['id']} id="id-1" value="1" checked={selected_title  === 1} onChange={setSelect} />
                        &nbsp;{props.data['longest_app']+":"+props.data['longest_title']} </label>
                    </div>
                    <div className="audio_title_label">
                        <label>
                            <input type="radio" name={"audio_titles"+props.data['id']} id="id-2" value="2" checked={selected_title  === 2} onChange={setSelect} />
                            &nbsp;<input type="text" className="audio_input_app" id="id-3-a" placeholder={props.data['another_app']} onChange={handleApp}></input> 
                            &nbsp;<input type="text" className="audio_input_title" id="id-3-t" placeholder={props.data['another_title']} onChange={handleTitle}></input>
                        </label>
                    </div>
                </div>
                <div className="audio_show_policy">
                        <label><input type="radio" name={"audio_show_policy"+props.data['id']} id="id-audio-front" value="0" checked={show_policy === 0} onChange={setPolicy}></input>
                        &nbsp;Audio優先 </label>
                        <label><input type="radio" name={"audio_show_policy"+props.data['id']} id="id-audio-back" value="1" checked={show_policy  === 1} onChange={setPolicy}></input>
                        &nbsp;Window優先 </label>
                        <label><input type="radio" name={"audio_show_policy"+props.data['id']} id="id-audio-ignore" value="2" checked={show_policy  === 2} onChange={setPolicy}></input>
                        &nbsp;無効 </label>
                </div>
                <div className="audio_save">
                    <Button variant="outline-secondary" size="sm" style={{marginLeft: "20px"}} onClick={setSettings}> 保存 </Button>
                </div>
            </div>

        );
    }
}

export default AudioActivityTag;