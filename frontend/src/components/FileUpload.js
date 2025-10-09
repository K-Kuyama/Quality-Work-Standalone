import { useCallback , useMemo, useState} from 'react';
import { useDropzone } from 'react-dropzone';
import Button from 'react-bootstrap/Button';
import Cookies from "universal-cookie";
import Settings from "../Settings";

const baseStyle = {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    width: "40%",
    height: 60,
};
const borderNormalStyle = {
    border: "2px dotted #888",
    backgroundColor: "rgba(255, 255, 255, 0.95)"
};
const borderDragStyle = {
    border: "3px solid #00f",
    transition: 'border .5s ease-in-out',
    backgroundColor: "rgba(255, 255, 255, 0.45)"
};


//const cookies = new Cookies();
  
  
  


function FileUpload(props) {
	const [isVisible, setVisibility] = useState(false);
	const [csv_data, setCSV] = useState([]);
	const [csv_info, setInfo] = useState([]);
	const [target_file, setFile] = useState([]);
	//const [userid, setUserid] = useState(0);
	
	const setChanged = props.setChanged;
	
    const onDrop = useCallback((acceptedFiles) => {
        // Do something with the files
        //console.log('acceptedFiles:', acceptedFiles);
        let file = acceptedFiles[0];
        setFile(file);
        let data;
        readCSVFile(file);
		setVisibility(true);
    }, []);
    
    const { getRootProps, getInputProps, isDragActive, open, acceptedFiles } = useDropzone({
		onDrop,
        noClick: true
    });
    
    const style = useMemo(() => (
        { ...baseStyle, ...(isDragActive ? borderDragStyle : borderNormalStyle)}
    ), [isDragActive]);
    
    const files = useMemo(() => 
        acceptedFiles.map((file) => (
            <li key={file.path}>
                {file.path} - {file.size} bytes
            </li>
        )
    ), [acceptedFiles]);
    
    
/*    
    useEffect(() => {
        const token = cookies.get('csrftoken')
        console.log("csrftoken:", token);
        fetch("/account/api-whoami",{
					credentials: "same-origin",
				}
		)
        .then(response => {
			return response.json();
		})
		.then(result =>{
			const txt = JSON.stringify(result, null,' ');
			console.log('---Success ---');
			console.log(txt);
			let res = JSON.parse(txt);
			console.log(res['userid'])
			setUserid(res['userid'])
		})
    },[])
*/
    
    
    const sendFormData = (e) =>{
    	const formData = new FormData();
    	const n_date = new Date();
    	//formData.append('user_id', userid);
    	formData.append('fileName', target_file.path);
    	formData.append('uploadTime', n_date.toISOString());
    	formData.append('contents', target_file);
    	formData.append('startTime', csv_info[0]);
		formData.append('endTime', csv_info[1]);
		formData.append('dataCount', csv_info[2]);
		formData.append('status', "未反映");
		//console.log("form", formData);
		let cookies = new Cookies();
		let token = cookies.get('csrftoken')
		let target = Settings.HOME_PATH+'/api/Activity/file_upload/'
		if(Settings.DEVELOP){
			target = Settings.DEVELOPMENT_HOME_PATH+'/api/Activity/file_upload/'
		}
		fetch(target, {
			method : 'POST',
			credentials: "same-origin",
			headers: {
					'X-CSRFToken': token,
				},
			body : formData,
			}
		)
		.then(result =>{
			console.log(result);
			setChanged(true);
			setVisibility(false);
		})
		.catch(error =>{		
			console.error(error);
			setVisibility(false);
		})
    }
    
//    const infoBoard = useMemo(() =>{
//    	<div className="info_board">
//    		<label>From: {csv_info[0]} &nbsp; To: {csv_info[1]} &nbsp;データ数{csv_info[2]}</label>
//    		<Button variant="secondary" className="upload_b" onClick={sendFormData}><i class="bi-upload"></i>アップロード</Button>
//    		<Button variant="secondary" className="cancel_b" onClick={setVisibility(false)}><i class="bi-allow-left-square"></i>中止</Button>
//    	</div>
//    },[csv_info])
    

 // FileReader APIを使ってファイルを読み込む関数
	const readCSVFile = (file) =>{
	    const reader = new FileReader();
    
    	// 読み込みが完了したら、CSVデータを処理
    	reader.onload = function (event) {
    		const csvData = event.target.result;
      		const result = processData(csvData);
      		setInfo(result);

    	};

    	// ファイルをテキストとして読み込む
    	reader.readAsText(file);
  	}
 
 
// CSVデータを処理する関数
	const processData = (csvData) =>{
    	// CSVデータを行に分割
    	const rows = csvData.split("\n");

    	// 各行をカンマで分割し、2次元配列に変換
    	const data = rows.map(row => row.split(","));
    	// 最後の行は空行になっているので、これを除外
    	data.length = data.length-1;
    	//最初の時刻と最後の時刻とデータ数を取り出す
    	let count = data.length;
    	const dataInfo = [data[0][0], data[count-1][0], count];
    	return dataInfo;
  	}
   
   return (
    	<div className="file_drop_area">
        	<div  {...getRootProps({ style })} >
         		<input {...getInputProps()} />
            		{
               	 isDragActive ?
                    <p>Drop the files here ...</p> :
                    <p>データファイルをここにドラッグ＆ドロップするか、右のフォルダからファイルを選択</p>
            		}
        		 <Button variant="secondary" onClick={open}><i class="bi-folder2"></i></Button>
        	</div>
        	{isVisible ?
 			<div className="info_board">
 				<div className="file_contents_info">
 					<label>From: {csv_info[0]} </label>
 					<label>To: {csv_info[1]} </label>
 					<label>データ数{csv_info[2]}</label>
 				</div>
    			<Button variant="primary" className="upload_b" onClick={(e)=> sendFormData(e)} ><i class="bi-upload" ></i>アップロード</Button>
    			<Button variant="secondary" className="cancel_b" onClick={(e)=> setVisibility(false)} ><i class="bi-arrow-left-square"></i>中止</Button>
    		</div>
    		: <></>}
        </div>
    	)

   

}

export default FileUpload;