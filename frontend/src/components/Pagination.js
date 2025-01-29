// import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';

function Pagination(props){

/*
	function handleClickPrev(event){
		props.handler(props.response['previous']);
	};
	
	function handleClickNext(event){
		props.handler(props.response['next']);
	};
*/

	// ボタンクリックの場合に呼び出される
	function handleClick(item){
		props.handler(props.response[item]);
	}

	return(
		<div className="pagenation_box">
			<ul className="cpanel">
				<Button variant="light" size="sm"  onClick={() => handleClick('previous')} id="pvB"> <i class="bi bi-caret-left-fill"></i> </Button>
				{/* <button type="button" onClick={() => handleClick('previous')}>
					前へ
				</button> */}
				<i>
					{props.response['current']}/{props.response['final']} 
				</i>
				<Button variant="light" size="sm"  onClick={() => handleClick('next')} id="nxB"> <i class="bi bi-caret-right-fill"></i> </Button>
				{/* <button type="button" onClick={() => handleClick('next')}>
					次へ
				</button> */}
			</ul>
		</div>
	);

}

export default Pagination;