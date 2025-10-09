import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import CategoryDefEditor from './CategoryDefEditor';
import RegisteredActivities from './RegisteredActivities';

function CategoryButtonListActivities(props){
    // 登録済みアクティビティの編集画面をModalで表示する

    const [cname, setCname]= useState("undefined");
    const handleClose = props.handler;
    const handleChangeCategory = props.def_change_handler;

    const closeMyself = () =>{
        handleClose(false);
    }


    //リスト表示する内容(登録済みアクティビティ)をpropsから取り出す
    const getCategoryActivities = () =>{
        if (props.categories.length >0 && props.cid != 0){
            let clist = props.categories.filter((c) => c['id']==props.cid);
            if(clist.length>0){
                return clist[0]['activities']
            } else {
                return [];
            }
        } else {
            return [];
        }
    }

    /***  レンダリング関連関数 ***/

    const printEditor = () =>{
        if(props.cid == 0 || props.category == undefined){
            return (<></>);
        } else {
            return(
                <>
                    <div className="registered-pane">
                        <RegisteredActivities activities={getCategoryActivities()} handler={handleChangeCategory} no_accordion={true} />
                    </div>
                </>
            )
        }
    }



    return(
        <Modal show={props.show} onHide={handleClose} size="lg" centered>
            <Modal.Header className="custom-modal" closeButton>
                <Modal.Title className="custom-modal-title">登録済みアクティビティの編集</Modal.Title>
            </Modal.Header>
            <Modal.Body className="lm_modal">
            {printEditor()}
            
            </Modal.Body>
            <Modal.Footer className="custom-modal">
                <Button className="btn-sm" variant="secondary" onClick={closeMyself}>閉じる</Button>
            </Modal.Footer>
        </Modal>
    )

}

export default CategoryButtonListActivities;