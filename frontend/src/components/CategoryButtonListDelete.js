import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Cookies from "universal-cookie";
import Settings from "../Settings";

function CategoryButtonListDelete(props){
    // カテゴリー削除確認画面をModalで表示する

    const [cname, setCname]= useState("undefined");
    const handleClose = props.handler;
    const setDefChange = props.def_change_handler;


    const closeMyself = () =>{
        handleClose(false);
    }

    const deleteCategory = (id) => {
        //カテゴリーのデータベースからの削除
        let cookies = new Cookies();
        let token = cookies.get('csrftoken')
        let target = Settings.HOME_PATH+'/api/user_def/Category/'
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/api/user_def/Category/'
        }
        fetch(target+id+"/", {
            method : 'DELETE',
            credentials: "same-origin",
            headers: {
                    'Content-Type' : 'application/json',
                    'X-CSRFToken': token,
                }	
            }
        )
        .then(response => {
            setDefChange(true);	
        })
        .catch(error =>{
            console.error(error);
        })
    
    }

    //Modal（自分自身）をクローズ
    const deleteClose = () =>{
        deleteCategory(props.cid);
        closeMyself();
    }

    const getCategory = () =>{
        //console.log(props.categories);
        //console.log(props.cid);
        if (props.categories.length >0){
            let clist = props.categories.filter((c) => c['id']==props.cid);
            return clist[0]
        } else {
            return null;
        }
    }

    const printInfo = () => {
        if(props.cid == 0){
            return (<></>);
        }else {
            //console.log(props.categories);
            if(props.categories){
                let anum =0;
                let knum =0;
                let cname ="undefined" ;
                let c = getCategory()
                //console.log(c);
                if(c){
                    anum = c.activities.length;
                    knum = c.key_words.length;
                    cname = c.name;
                }
                return(
                    <div className="del-info-body">
                    <label className="del-info-name">{cname}</label>
                    <hr size="2" color="white"></hr>
                    <label className="del-info-item">アクティビティが {anum}個登録されています</label>
                    <label className="del-info-item">キーワードが {knum}個登録されています</label>
                    </div>
                )
            }
        }
    }


    return(
        <Modal show={props.show} onHide={handleClose} size="lg" centered>
            <Modal.Header className="custom-modal" closeButton>
                <Modal.Title className="custom-modal-title">このカテゴリーを削除しますか？</Modal.Title>
            </Modal.Header>
            <Modal.Body className="lm_modal">
            {printInfo()}
            
            </Modal.Body>
            <Modal.Footer className="custom-modal">
                    <Button className="btn-sm" variant="primary" onClick={deleteClose}>削除</Button>
                    <Button className="btn-sm" variant="secondary" onClick={closeMyself}>閉じる</Button>
                </Modal.Footer>
        </Modal>
    )

}

export default CategoryButtonListDelete;