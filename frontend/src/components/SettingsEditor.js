import React, { useState, useEffect, useContext } from 'react';
import Button from 'react-bootstrap/Button';
import Cookies from "universal-cookie";
import Settings from "../Settings";

function SettingsEditor(props){

    const titles = {"audio":"オーディオ設定"}
    const [items, setItems] = useState([])
    const [requestBody, setRequestBody] = useState({});
    const [haveData, setHaveData] = useState(false); 
    const [redraw, setRedraw] = useState(false)


    const reset = () =>{
        setItems([]);
        setRedraw(true);
    }

    const getSettings = () => {
        let query = new URLSearchParams({"file":props.category});
        let target = Settings.HOME_PATH+'/api/Activity/DaemonSettings/1/?'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/DaemonSettings/1/?'
        }
        fetch(target + query,{
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
            setItems(Object.entries(res));
            setHaveData(true);
        })
        .catch(error =>{
            setHaveData(false);
            console.error('----Error---');
            console.error(error);
        })
    }

    const sendSettings = (target_items) => {
        console.log("target_items =>", target_items)
        let cookies = new Cookies();
        let token = cookies.get('csrftoken')
        let query = new URLSearchParams({"file":props.category});
        let target = Settings.HOME_PATH+'/api/Activity/DaemonSettings/1/?'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/DaemonSettings/1/?'
        }
        fetch(target+query,
			{
				method: "PATCH",
				credentials: "same-origin",
				headers: {
					'Content-Type' : 'application/json',
					'X-CSRFToken': token,
				},
				body: JSON.stringify(target_items)
			}
		)
		.then(response => {
			return response.json();
		})
		.then(result =>{
            const txt = JSON.stringify(result, null,' ');
            let res = JSON.parse(txt);
            //console.log(res);
            setItems(Object.entries(res));
            setRequestBody({});
            setHaveData(true);
		})
		.catch(error =>{
			console.error('----Error---');
			console.error(error);
		})
    }

    const setEnable = (e) => {
        console.log("checkbox ", e.target.checked);
        console.log("checked value =", e.target.value);
        let txt = document.querySelector("#stx-"+e.target.value);
        if(e.target.checked){
            txt.disabled = false;
        } else {
            txt.disabled = true;
        }
    }

    const setChangedValues = () => {
        let items = document.querySelectorAll("input[name=c_item]:checked");
        let request_body = {}
        for (const item of items){
            let lbl = document.querySelector("#slb-"+item.value);
            console.log(lbl);
            let txt = document.querySelector("#stx-"+item.value);
            console.log(lbl.getAttribute("value"));
            console.log(txt.value);
            if(txt.getAttribute("dataType") == "number"){
                request_body[lbl.getAttribute("value")] = Number(txt.value);
            }else{
                request_body[lbl.getAttribute("value")] = txt.value;
            }
        }
        console.log(request_body);
        setRequestBody(request_body);
        if(Object.keys(request_body).length > 0){
            setItems([]);  
            sendSettings(request_body);
            //setItems([]);
            //setRedraw(true);
        }
    }



    useEffect(() => {
        getSettings();
        setRedraw(false);
    },[props, redraw])


    if (!haveData) {
		return <div>Loading...</div>
	} else{
        return(
            <div className="SettingsEditoer">
                <label className="settings-title"> {titles[props.category]} </label>
                <hr size="5" width="100%" color="white" ></hr>
                {
                    items.map((item, idx) =>{
                        return (<tr>
                                    <td width="24px"><input type="checkbox" name="c_item" value={idx} onChange={(e)=>setEnable(e)} /></td>
                                    <td width="220pt"><label className="setting-label" id={"slb-"+idx} value={item[0]}>{item[0]}</label></td>
                                    <td width="240pt"><input type="text" className="setting-text" id={"stx-"+idx} defaultValue={item[1]} dataType={typeof(item[1])} disabled></input></td>
                        </tr>)
                    })
                }
                <div className="ce_header">
                    <Button type="button" className="btn btn-ppheader" data-bs-toggle="button" size="sm" onClick={(e)=> setChangedValues()} >
                        保存
                    </Button>
                    <Button type="button" className="btn btn-dlt-ppheader" data-bs-toggle="button" size="sm" onClick={(e)=> reset()} >
                        Reset
                    </Button>
                </div>
            </div>
        );
    }
}

export default SettingsEditor;