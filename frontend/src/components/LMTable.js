import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Cookies from "universal-cookie";
import 'bootstrap-icons/font/bootstrap-icons.css';
import LMCreateModal from "./LMCreateModal";
import Settings from "../Settings";

function LMTable(props){
    const [pid, setPid] = useState(props.pid);
    const [haveData, setHaveData] = useState(false); 
    const [lm_list, setList] = useState([]);

    const [show, setShow] = useState(false);
    const [changed, setChanged] = useState(false);

    const handleClose = () =>{
        setShow(false);
    }

    const activate_lm = (e) =>{
        let target = Settings.HOME_PATH+'/api/AI/activate_predictor/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/AI/activate_predictor/'
        }
        let params ={p_id : props.p_id};
        let query = new URLSearchParams(params);
        fetch(target+ e.target.value+'/?'+query,{
                method: 'PUT',
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
            setList(res);
            setHaveData(true);
        })
        .catch(error =>{
            setHaveData(false);
            console.error('----Error---');
            console.error(error);
        })        
    }

    const delete_lm = (e) =>{
        let target = Settings.HOME_PATH+'/api/AI/destroy_activity_predictor/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/AI/destroy_activity_predictor/'
        }
        let params ={p_id : props.p_id};
        let query = new URLSearchParams(params);
        fetch(target+ e.target.value+'/?'+query,{
                method: 'DELETE',
                credentials: "same-origin",
            }
        )
        .then(response => {
            console.log("response status",response.status);
            return response.json();
        })
        .then(result =>{
            const txt = JSON.stringify(result, null,' ');
            let res = JSON.parse(txt);
            console.log(res);			
            setList(res);
            setHaveData(true);
        })
        .catch(error =>{
            console.error('----Error---');
            console.error(error);
        })        
    }

    const getBordefColor = (using) =>{
        //console.log('using', using);
        if(using == true){
            return 'rgba(255, 255, 255, 0.75)';
        } 
        else{
            return '#27293d';
        }
    }

    const data_duration = (start, end) =>{
        if(start == null){
            if(end == null){
                return(<label className="duration_kind">データ期間 : 全期間</label>)
            }
            else {
                return(
                    <>
                    <label className="duration_kind">データ期間 : </label>
                    <label className="start_end">〜{end.slice(0,10)}</label>
                    </>
                )
            }
        } else {
            if(end == null){
                return(
                    <>
                    <label className="duration_kind">データ期間 : </label>
                    <label className="start_end">{start.slice(0,10)}〜</label>
                    </>
                )
            } else {
                return(
                    <>
                    <label className="duration_kind">データ期間 : </label>
                    <label className="start_end">{start.slice(0,10)}〜{end.slice(0,9)}</label>
                    </>
                )
            }
        }
    }

    useEffect(() =>{
        if(props.p_id != 0){
            let target = Settings.HOME_PATH+'/api/AI/activity_predictors/?'
            if(Settings.DEVELOP){
                target = Settings.DEVELOPMENT_HOME_PATH+'/api/AI/activity_predictors/?'
            }
            let params ={p_id : props.p_id};
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
                let res = JSON.parse(txt);
                //console.log(res);			
                setList(res);
                setHaveData(true);
                setChanged(false);
            })
            .catch(error =>{
                setHaveData(false);
                console.error('----Error---');
                console.error(error);
            })
        }

    },[props, changed])

    if(props.p_kind != 'PerspectiveModel'){
    return (
        <div className="lm_table">
            <div className="lm_table_title">
                AIモデル一覧
            </div>
            <div className="lm_create_button">
                <Button variant="primary" size="sm"  onClick={setShow}> モデル生成 </Button>
            </div>
            <div className="lm_info_h">
                <div className="lm_title_h">タイトル・生成時刻</div>
                <div className="lm_numbers_h">諸元</div>
                <div className="lm_score_h">評価結果</div>
                <div className="lm_buttons"></div>
            </div>
            <div className="lm_info_box">
                {lm_list.map((obj) => {
                    return (
                        <div className="lm_info" style={{borderColor: getBordefColor(obj['using'])}}>
                            <div className="lm_title"> 
                                <label className="lm_name">{obj['name']}</label>
                                <label className="lm_date">{obj['created_dtime'].slice(0,19).replace('T',' ')}</label>
                            </div>
                            <div className="lm_numbers"> 
                                <label className="lm_labels">ラベル数:&nbsp;{obj['num_of_labels']}</label>
                                <label className="lm_datas">学習データ数:&nbsp;{obj['num_of_learning_data']}</label>
                                {data_duration(obj['data_start'], obj['data_end'])}
                            </div>
                            <div className="lm_score">{obj['score']}</div>
                            <div className="lm_buttons">
                                <Button variant="outline-primary" size="sm" value={obj['id']} onClick={activate_lm}> 適用 </Button>
                                <Button variant="outline-secondary" size="sm" value={obj['id']} onClick={delete_lm}> 削除 </Button>
                            </div>
                        </div>
                    )
                })}
            </div>
            <LMCreateModal show={show} p_id={props.p_id} handler={handleClose} set_changed={setChanged} activate={activate_lm}/>
        </div>
    )
    }
}

export default LMTable;