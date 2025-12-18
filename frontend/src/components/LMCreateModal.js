import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import DatePicker, { registerLocale } from "react-datepicker";
import Cookies from "universal-cookie";
import 'bootstrap-icons/font/bootstrap-icons.css';
import { getBothEnds } from "./utils"
import Settings from "../Settings";
import {RouletteSpinnerOverlay} from "react-spinner-overlay";

function LMCreateModal(props){
      
    //const [show, setShow] = useState(false);
    const handleClose = props.handler;
    const setChanged = props.set_changed;
    const handleActivate = props.activate;
    //const handleShow = () => setShow(true);

    const [data_kind, setKind] = useState("all");
    const [start, setStart] = useState(null);
    const [end, setEnd] = useState(null);
    const [list, setList] = useState([]);
    const [result, setResult] = useState(false);
    const [status, setStatus] = useState(0);
    const [processing, setProcessing] = useState(false); //スピナーの表示状態

    const setKindChange = (e) =>{
        setKind(e.target.value);
    }

    const closeMyself = () =>{
        setKind('all');
        setStart(null);
        setEnd(null);
        setResult(false);
        setStatus(0);
        setList([]);
        handleClose();
    }

    const closeWithActicate = (e) =>{
        handleActivate(e);
        closeMyself();
    }

    const createModel = (e) =>{
        setProcessing(true);
        let target = Settings.HOME_PATH+'/api/AI/create_activity_predictor/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/AI/create_activity_predictor/'
        }
        let cookies = new Cookies();
        let token = cookies.get('csrftoken')
        console.log('start:',start)
        console.log('end:',end)

        let params ={p_id: props.p_id}
        if(start == null){
            if(end != null){
                let ed =  getBothEnds(new Date(end))[1];
                params.end = ed;
            }
        } else {
            let sd = getBothEnds(new Date(start))[0];
            if(end == null){
                params.start = sd;
            }
            else{
                let ed =  getBothEnds(new Date(end))[1];
                params.start = sd;
                params.end = ed;
            }
        }

        
        //let params ={p_id : props.p_id, start : sd, end : ed};
        let query = new URLSearchParams(params);
        fetch(target+'?'+query,{
                method: 'POST',
                credentials: "same-origin",
                headers: {
					'X-CSRFToken': token,
				},
            }
        )
        .then(response => {
            console.log("response status",response.status);
            setStatus(response.status);
            setResult(true);
            return response.json();
        })
        .then(result =>{
            const txt = JSON.stringify(result, null,' ');
            let res = JSON.parse(txt);
            console.log(res);			
            setList(res);
            setChanged(true);
            setProcessing(false);
        })
        .catch(error =>{
            console.error('----Error---');
            console.error(error);
            setProcessing(false);
        })
        
    }

    const printResult = () =>{
        if(result == true){
            //setProcessing(false);
            if(status == 201){
                return(
                    <div className="result_success">
                        <hr size="5" color="white" ></hr>
                        <div className="result_message">生成完了しました</div>
                        <div className="result_number"> 学習データ数:&nbsp;{list['num_of_learning_data']} </div>
                        <div className="result_score"> {list['score']} </div>
                        {/*<div className="result_button"> 
                            <Button variant="outline-primary" value={list['id']} onClick={closeWithActicate}>適用</Button>
                        </div>*/}
                    </div>
                )
            } else {
                return(
                    <div>生成に失敗しました。&nbsp;{list['detail']}</div>
                )
            }
        }else {
                return(
                    <div className="result_button"> 
                        <Button variant="primary" onClick={createModel}>生成</Button>
                    </div>
                )
        }
    }

    const printButtons = () =>{
        if(result == true && status == 201){
            return(
                <Button variant="primary" value={list['id']} onClick={closeWithActicate}>適用</Button>
            )
        }
    }

    return(
        <Modal show={props.show} onHide={handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>学習モデルの生成</Modal.Title>
            </Modal.Header>
            <Modal.Body className="lm_modal">
                <div className="lm_data_params">
                    <label className="params_title">学習データ</label>
                    <label>
                        <input type="radio" name="lditems" id="id-0" value="all" checked={data_kind == "all"} onChange={setKindChange} />
                        &nbsp;全てのアクティビティ情報を使う
                    </label>
                    <label>
                        <input type="radio" name="lditems" id="id-1" value="designated" checked={data_kind == "designated"} onChange={setKindChange} />
                        &nbsp;期間を指定する
                    </label>
                    <div className="lm_time_period">
                        <DatePicker dateFormat="yyyy/MM/dd" locale='ja' className="lms_datepicker" selected={start} value={start} onChange={setStart} />
                        <label>&nbsp;〜&nbsp;</label>
                        <DatePicker dateFormat="yyyy/MM/dd" locale='ja' className="lme_datepicker" selected={end} value={end} onChange={setEnd} />
                    </div>
                </div>
                <div className="lm_result">
                    {printResult()}
                </div>
                <RouletteSpinnerOverlay loading={processing} overlayColor="rgba(0,153,255,0.5)" message="モデル生成中" />
            </Modal.Body>
            <Modal.Footer>
                {printButtons()}
                <Button variant="secondary" onClick={closeMyself}>閉じる</Button>
            </Modal.Footer>
        </Modal>
    )

}

export default LMCreateModal;