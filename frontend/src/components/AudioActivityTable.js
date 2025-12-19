import React, { useState, useEffect , useContext } from 'react';
import AudioActivityTag from "./AudioActivityTag";
import { getBothEnds } from "./utils"
import { ShowPolicyContext } from '../Context';
//import Cookies from "universal-cookie";
import Settings from "../Settings";

function AudioActivityTable(props){

    const [data, setData]= useState([]);
    const [haveData, setHaveData] = useState(false); 
    const [target_date, setDate] = useState(props.target_date);
    const [item, setItem] = useState(props.item);
    const [font_color, setColor] = useState("rgba(255, 255, 255, 0.15)")

    const ctx = useContext(ShowPolicyContext);

    /* propsに変更があった時に呼び出される */
    
    useEffect(() => {
        // props.idv_policy === 3以外の場合「個別設定」部分をマスク
        let elements = document.querySelectorAll(".audio_show_policy_t");
        if (ctx.policy === 3){
            elements.forEach((e) => {
                e.disabled = false;
                setColor("rgba(255, 255, 255, 0.55)")
            })}
        else {
            elements.forEach((e) => {
                e.disabled = true;
                setColor("rgba(255, 255, 255, 0.15)")
            })
        }
        //console.log("policy->", props.idv_policy)
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


	if (!haveData) {
		return <div>Loading...</div>
	} else{
		return(
			<div className="audio_list">	
                <div className="audio_activity_tag">
                    <div className="audio_time_column_t">開始時間/終了時間</div>
                    <div className="audio_duration_t">継続時間</div>
                    <div className="audio_title_column_t">タイトル</div>
                    <div className="audio_show_policy_t" style={{color: font_color}}>個別設定</div>
                    <div className="audio_save_t"></div>
                </div>
				{
                    data.map((a) => {
                        return(
                            <AudioActivityTag data={a} idv_policy={props.idv_policy} />
                        );
                    })
                }
			</div>
		);
	}

}

export default AudioActivityTable;