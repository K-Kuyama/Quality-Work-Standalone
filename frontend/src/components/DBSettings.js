import React, { useState, useEffect } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import Button from 'react-bootstrap/Button';
import DBLoader from "./DBLoader";
//import Cookies from "universal-cookie";
import Settings from "../Settings";

function DBSettings(props){

    const [result, setResult] = useState("");

    const initDB = (e) =>{

        let target = Settings.HOME_PATH+'/system/init_db/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/system/init_db/'
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
            //console.log('---Success ---');
            //console.log(txt);
            let res = JSON.parse(txt);
            setResult(res)

        })
        .catch(error =>{
            console.error('----Error---');
            console.error(error);
        })
    }


    return(
        <div className="db_settings">
            <label className="settings-title"> データベース設定 </label>
            <hr size="5" width="100%" color="white" ></hr>
            <Accordion className="db-accordion">
                <Accordion.Item eventKey="0">
                    <Accordion.Header className="db-accordion-header">データベース移行</Accordion.Header>
                    <Accordion.Body>
                        <DBLoader />
                    </Accordion.Body>
                </Accordion.Item>
                <Accordion.Item eventKey="2">
                    <Accordion.Header className="db-accordion-header">データベース初期化</Accordion.Header>
                    <Accordion.Body>
                        <label>データベースをインストール時の状態に戻します　</label>
                        <Button variant="primary" className="upload_b" onClick={(e)=> initDB(e)} >初期化</Button>
                        <label>{result}</label>
                    </Accordion.Body>
                </Accordion.Item>
            </Accordion>
        </div>
    )


}

export default DBSettings;