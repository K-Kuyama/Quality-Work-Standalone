import React, { useState } from 'react';
import FileUpload from "./FileUpload";
import DBInfoPanel from "./DBInfoPanel";

/* アクティビティーリストページ */
function FileLoader(){
    const [target_date, setDate] = useState(new Date());
    const [item, setItem] = useState("event_list");

	const [changed, setChanged] = useState(false);


	return(
		<>
            <DBInfoPanel setChanged={setChanged} />
            <hr size="5" width="100%" color="white" ></hr>
            <FileUpload setChanged={setChanged} />    
		</>
	)

}

export default FileLoader;