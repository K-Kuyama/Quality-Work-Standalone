import React, { useState, useEffect } from 'react';
import Settings from "../Settings";

function DBStat(props){

    const [dbi, setDBInfo] = useState(null);
    const [haveData, setHaveData] = useState(false);
    const setChanged = props.setChanged;

    const tables_def = {activity:"アクティビティ", audio:"音声アクティビティ"} 

    useEffect(() => {

        let target = Settings.HOME_PATH+'/api/Activity/activity_db_info/1/?'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/activity_db_info/1/?'
        }
        let params = {table: props.table};
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
            setDBInfo(res);
            setHaveData(true);
            
        })
        .catch(error =>{
            console.error('----Error---');
            console.error(error);
        })
    }, [props]);

    if(haveData){
	return(
        <div className="db_status">
            <label>{tables_def[props.table]}データ情報</label>
                <table className="db_table">
                    <tr><td>先頭データ</td><td>{dbi['startTime']}</td></tr>
                    <tr><td>最終データ</td><td>{dbi['endTime']}</td></tr>
                    <tr><td>データ数</td><td>{dbi['count']}</td></tr>
                </table>
        </div>
        )
    }
}

export default DBStat;