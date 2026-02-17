import React, { useState, useEffect } from 'react';
import Settings from "../Settings";

function TextDocArea(props){

    const [doc, setDoc] = useState(props.text_name);
    const [text, setText] = useState("")

    useEffect(() =>{
        let target = Settings.HOME_PATH+'/static/licenses/'+props.text_name
        if(Settings.DEVELOP){
            target = Settings.DEVELOPMENT_HOME_PATH+'/static/licenses/'+props.text_name
        }			
        fetch(target,{
                    credentials: "same-origin",
                }
        )
        .then(response => {
            return response.text();
        })
        .then(data =>{
            setText(data);
        })
        .catch(error =>{
            console.error('----Error loading text file---');
            console.error(error);
        })
    },[props])

    return (
        <div className="license_text">
            <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {text}
            </pre>
        </div>
    )

}

export default TextDocArea;