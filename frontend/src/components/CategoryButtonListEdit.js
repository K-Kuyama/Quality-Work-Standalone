import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import CategoryDefEditor from './CategoryDefEditor';
import RegisteredActivities from './RegisteredActivities';

function CategoryButtonListEdit(props){
    // カテゴリーのタイトルと色を変更するための編集画面をModalで表示する

    const [cname, setCname]= useState("undefined");
    const handleClose = props.handler;
    const handleChangeCategory = props.def_change_handler;

    const closeMyself = () =>{
        handleClose(false);
    }



    const printEditor = () =>{
        if(props.cid == 0 || props.category == undefined){
            return (<></>);
        } else {
            return(
                <>
                    <div className="def-editor-pane">
                    {/*<CategoryDefEditor id="0" pid={getCategoryPid()} name={getCategoryName()} color={getCategoryColor()} handler={handleChangeCategory} />*/}
                    <CategoryDefEditor id={props.cid} pid={props.category['perspective']} name={props.category['name']} color={props.category['color']} handler={handleChangeCategory} />
                    </div>
                </>
            )
        }
    }


    return(
        <Modal show={props.show} onHide={handleClose} size="lg" centered>
            <Modal.Header className="custom-modal" closeButton>
                <Modal.Title className="custom-modal-title">カテゴリーの編集</Modal.Title>
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

export default CategoryButtonListEdit;