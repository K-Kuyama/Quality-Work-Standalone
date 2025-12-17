import React, { useContext, useState, useEffect } from 'react';
import { ShowPolicyContext } from '../Context';
import Settings from "../Settings";
import Cookies from "universal-cookie";

function AudioSettings(props){
    const [haveData, setHaveData] = useState(false)
    const [policy, setPolicy] = useState(0)
    const [id, setID] = useState(1)

    const setParentPolicy = props.policy_handler;

    const c_list = [[0,"無効"],[1,"Audio優先"],[2,"Window優先"],[3,"個別設定"]]; 

    const ctx = useContext(ShowPolicyContext);

    const setGlobalPolicy = (d) =>{
        let item = Number(d.target.value);
        updateDB(item);
        setPolicy(item);
        setParentPolicy(item);
        ctx.updatePolicy(item);
        console.log("selected item :"+item)

    }

    const updateDB = (item) => {
        let additional_str =id+"/";
        let method_str = "PATCH";
        let target = Settings.HOME_PATH+'/api/SystemSettings/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/SystemSettings/'
        }
        let request_body ={audio_activity_policy: item};
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


    useEffect(() => {
        let target = Settings.HOME_PATH+'/api/SystemSettings/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/SystemSettings/'
        }
                    
        fetch(target,{
            credentials: "same-origin",
            }
        )
        .then(response => {
            return response.json();
        })
        .then(result =>{
            const txt = JSON.stringify(result, null,' ');
            let res = JSON.parse(txt);
            console.log(res);
            setPolicy(res[0]['audio_activity_policy']);
            setParentPolicy(res[0]['audio_activity_policy']);
            setID(res[0]['id'])
            setHaveData(true);
        })
        .catch(error =>{
            setHaveData(false);
            console.error('----Error---');
            console.error(error);
        })
    },[props])

    if (!haveData) {
		return <div>Loading...</div>
    }
    else{
        return(
            <div className="audio_settings_panel">
                <label className="date_title" key="item_title-1">表示設定</label>
                {c_list.map((condition) => {
                    return (
                        <label><input type="radio" name="items" id={"id-"+condition[0]} value={condition[0]} checked={condition[0] === policy} onChange={setGlobalPolicy} />
                        &nbsp;{condition[1]} </label>
                    )
                })}	
            </div>
        )
    }
}

export default AudioSettings;