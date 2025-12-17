import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';

function LMDeleteModal(props){
    // 使用中のpredictorを消去しようとした時に表示する確認用モーダル
    const handleDelete = props.delete_handler;
    const handleClose = props.close_handler;

    return (
        <div
            className="modal show"
            style={{ display: 'block', position: 'initial' }}
        >
            <Modal show={props.show} onHide={handleClose} centered>
                <Modal.Header closeButton>
                <Modal.Title>確認</Modal.Title>
                </Modal.Header>

                <Modal.Body>
                <p>適用中のモデルを削除しようとしています。本当に削除しますか？</p>
                </Modal.Body>

                <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>キャンセル</Button>
                <Button variant="primary" onClick={handleDelete}>削除</Button>
                </Modal.Footer>
            </Modal>
        </div>
  );
}

export default LMDeleteModal;