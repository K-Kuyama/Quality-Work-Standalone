import React, { useContext, useState, useEffect } from 'react';
import { ShowPolicyContext } from '../Context';
import Settings from "../Settings";
import Cookies from "universal-cookie";

function PerspectiveModelViewSettings(props){
    const [model_kind, setKind] = useState("");
    const [id, setId] = useState(props.p_id);

    const set_parent_kind = props.handler;

    const updateDB = (item) => {
        let additional_str =props.p_id+"/";
        let method_str = "PATCH";
        let target = Settings.HOME_PATH+'/api/user_def/Perspective/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/Perspective/'
        }
        let request_body ={categorize_model: item};
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
            const txt = JSON.stringify(result, null,' ');
            let res = JSON.parse(txt);
            //console.log("DBアップデートの結果 result= ", res);
        })
        .catch(error =>{
            console.error(error);
        })
    }

    const setChange = (d) =>{
        updateDB(d.target.value);
        //console.log("setChangeが呼ばれDBアップデートされた ->", d.target.value)
        set_parent_kind(d.target.value);
        setKind(d.target.value);

    }

    useEffect(() => {
        //console.log("propsが変更された ->",props);
        setKind(props.p_kind);
    },[props])

    return(
        <div className="pm_settings_panel">
            <label className="pm_settings_label">分類方法</label>
            <div className="perspective_model_view_settings">
                {/*<label className="date_title" key="item_title-1">カテゴライズ方法</label>*/}
                <label>
                    <input type="radio" name="cwitems" id="id-0" value="PerspectiveModel" checked={model_kind === null || model_kind == "PerspectiveModel" } onChange={setChange} />
                    &nbsp;キーワードマッチング&nbsp;&nbsp;
                </label>
                <label>
                    <input type="radio" name="cwitems" id="id-1" value="AIPerspectiveModel" checked={model_kind == "AIPerspectiveModel"} onChange={setChange} />
                    &nbsp;学習モデルによる推定：全て
                </label>
                <label>
                    <input type="radio" name="cwitems" id="id-2" value="AIPerspectiveModelHighPossibility" checked={model_kind == "AIPerspectiveModelHighPossibility"} onChange={setChange} />
                    &nbsp;学習モデルによる推定：高確度のみ
                </label>
            </div>
        </div>
    )
}

export default PerspectiveModelViewSettings;