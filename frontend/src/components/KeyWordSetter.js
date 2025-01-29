import React, { useState } from 'react';
import Button from 'react-bootstrap/Button';

function KeyWordSetter(props){
	const [isVisible, setVisibility] = useState(false);
	const setNewKeyWord = props.set_handler;
	const handleTextChange = props.text_handler;
	
	if(isVisible){
		return (
    			<div className="input_panel">
    				<div className="left_button_panel">
    					<Button variant="outline-light" size="sm" style={{margin: "6px", width: "80px"}} onClick={(e)=> setVisibility(false)}> <i class="bi bi-x-lg"></i> 閉じる</Button>
    				</div>
    				<div className="center_button_panel">
    					キーワード 
    					<input type="text" id="keyword_txt" style={{marginLeft: "10px", width: "50%"}} onChange={handleTextChange} ></input>
    					<Button variant="outline-secondary" size="sm" style={{marginLeft: "10px"}} onClick={(e)=> setNewKeyWord(props.flag)} > <i class="bi bi-caret-up-fill"></i> </Button>

    				</div>
    					
    			</div>
    			)
	} else{
		return(
					<div className="move_button_panel">
    					<Button variant="outline-light" size="sm" style={{margin: "6px", width: "80px"}} onClick={(e)=> setVisibility(true)}> <i class="bi bi-plus-lg"></i> 追加</Button>
    				</div>
    			)
	}
	
		
	
}

export default KeyWordSetter;