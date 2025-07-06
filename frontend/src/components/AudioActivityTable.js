import React, { useState, useEffect } from 'react';
import AudioActivityTag from "./AudioActivityTag";
import { getBothEnds } from "./utils"
//import Cookies from "universal-cookie";
import Settings from "../Settings";

function AudioActivityTable(props){

    const [data, setData]= useState([]);
    const [haveData, setHaveData] = useState(false); 
    const [target_date, setDate] = useState(props.target_date);
    const [item, setItem] = useState(props.item);

    /* propsに変更があった時に呼び出される */
    
    useEffect(() => {
        setDate(props.target_date);
        // 表示すべきターゲットデートがない場合は、サーバへの呼び出しをしない。
        if(target_date){		
            let date = new Date(props.target_date);
            let both_ends = getBothEnds(date);
            let d1 = both_ends[0];
            let d2 = both_ends[1];
            let params = {start : d1, end : d2};
            let target = Settings.HOME_PATH+'/api/AudioActivity/Activity/?'
                if(Settings.DEVELOP){
                    target = Settings.DEVELOPMENT_HOME_PATH+'/api/AudioActivity/Activity/?'
                }
            let query = new URLSearchParams(params);
            fetch(target+query,{
                    credentials: "same-origin",
                }
            )
            .then(response => {
                return response.json();
            })
            .then(result =>{
                const txt = JSON.stringify(result, null,' ');
                //console.log('---Success ---');
                //console.log(txt);
                let res = JSON.parse(txt);
                console.log(res);
                setData(res);
                setHaveData(true);
            })
            .catch(error =>{
                setHaveData(false);
                console.error('----Error---');
                console.error(error);
            })
        }
    },[props]);
    

    /*
    useEffect(() => {
        setData(
        [{'another_app': null,
        'another_title': null,
        'duration': 57,
        'end_time': '2025-04-13T08:00:30.583958+09:00',
        'id': 37,
        'longest_app': 'Terminal',
        'longest_title': 'article_sample — jupyter-notebook ▸ Python — 164×46',
        'selected': 0,
        'show_front': true,
        'start_app': 'Safari',
        'start_time': '2025-04-13T07:59:33.308195+09:00',
        'start_title': 'Pythonでウェブサービスを作ろう！ 初心者向けdjangoチュートリアル #1 - YouTube'},
       {'another_app': null,
        'another_title': null,
        'duration': 462,
        'end_time': '2025-04-13T08:08:23.939959+09:00',
        'id': 38,
        'longest_app': 'Safari',
        'longest_title': 'Pythonでウェブサービスを作ろう！ 初心者向けdjangoチュートリアル #1 - YouTube',
        'selected': 0,
        'show_front': true,
        'start_app': 'Terminal',
        'start_time': '2025-04-13T08:00:41.660752+09:00',
        'start_title': 'backend — poetry shell ▸ Python — 165×68'},
       {'another_app': null,
        'another_title': null,
        'duration': 377,
        'end_time': '2025-04-13T08:15:34.855811+09:00',
        'id': 39,
        'longest_app': 'Safari',
        'longest_title': 'Pythonでウェブサービスを作ろう！ 初心者向けdjangoチュートリアル #1 - YouTube',
        'selected': 0,
        'show_front': true,
        'start_app': 'Notes',
        'start_time': '2025-04-13T08:09:17.714228+09:00',
        'start_title': '第６章 Reactプログラミング'}
        ]
        );
        setHaveData(true);
    },[props])
    */


	if (!haveData) {
		return <div>Loading...</div>
	} else{
		return(
			<div className="audio_list">	
                <div className="audio_activity_tag">
                    <div className="audio_time_column_t">開始時間/終了時間</div>
                    <div className="audio_duration_t">継続時間</div>
                    <div className="audio_title_column_t">タイトル</div>
                    <div className="audio_show_policy_t">ポリシー</div>
                    <div className="audio_save_t"></div>
                </div>
				{
                    data.map((a) => {
                        return(
                            <AudioActivityTag data={a} />
                        );
                    })
                }
			</div>
		);
	}

}

export default AudioActivityTable;