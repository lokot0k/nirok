import {LoaderFunctionArgs, Navigate, useLoaderData, useNavigate} from "react-router-dom";
import {ChangeEventHandler, useEffect, useRef, useState} from "react";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {solid} from "@fortawesome/fontawesome-svg-core/import.macro";
import {ChupChupChup} from "./assets/ChupChupChup";
import {BurgZurgGurg} from "./assets/BurgZurgGurg";
import clsx from "clsx";

const xuy = ["cartwheel", "catch", "clap", "climb", "dive", "draw_sword", "dribble", "fencing", "flic_flac", "golf",
    "handstand", "hit", "jump", "pick", "pour", "pullup", "push", "pushup", "shoot_ball", "sit", "situp", "swing_baseball", "sword_exercise", "throw"]
const pizda = ["Колесо", "Поимка", "Хлопок", "Вскарабкивание", "Нырок", "Обнаживание меча", "Дриблинг", "Фехтование", "Рандат", "Гольф",
    "Стояние на руках", "Удар", "Прыжок", "Подбирание", "Наливание", "Подтягивание", "Толкание", "Отжимание", "Бросок мяча", "Присаживание", "Качание пресса", "Взмах битой", "Упражнение с мечом", "Бросание"]

const l10n = Object.fromEntries(xuy.map((v, i) => [v, pizda[i]]))

type Item = {
    videoSrc: string;
    thumbnailSrc: string;
    name: string;
    description: string;
    originalTag: string;
}

type Data = {
    [p: string]: string[]
}


export const loader = async (): Promise<Data | null> => {
    // ====== api request ========

    const response = await fetch("/api/do_good/", {
        method: "GET",
    })
    let x = await response.json();
    return response.ok ? x as Data : null;
}


function downloadFile(url: string, filename: string) {
    const link = document.createElement('a');
    link.href = `http://localhost:8000${url}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

type ViewMode = "ChupChupChup" | "BurgZurgGurg"

type PlayerProps = {
    close: () => void;
    next: () => void;
    prev: () => void;
    data: Item[];
    chosenImage: number;
}

const Player = ({close, data, chosenImage, prev, next}: PlayerProps) => {
    chosenImage = (chosenImage + data.length) % data.length

    return <div className="relative p-4 flex justify-center items-center">
        <div className="absolute -top-14 text-4xl text-main font-bold">
            {data[chosenImage].description}
        </div>
        <button className="absolute top-4 right-4 z-4 text-4xl text-main" onClick={close}><FontAwesomeIcon
            icon={solid("close")}/></button>
        <span className="mr-4 cursor-pointer text-4xl text-main" onClick={prev}>
            <FontAwesomeIcon icon={solid("chevron-left")}/>
        </span>
        <div className="aspect-[4/3] w-3/5 bg-black flex items-center">
            <video src={data[chosenImage].videoSrc} className="w-full" autoPlay loop/>
        </div>

        <span className="ml-4 cursor-pointer text-4xl text-main" onClick={next}>
            <FontAwesomeIcon icon={solid("chevron-right")}/>
        </span>
    </div>;
};

type ImagesViewProps = {
    images: Item[]
    chooseImage: (index: number) => void;
}

const ImageGrid = ({images, chooseImage}: ImagesViewProps) => <div className="grid grid-cols-5 -mt-2">
    {images.map((item, index) => <div key={index}
                                      className="relative m-2 cursor-pointer transition-transform hover:scale-105 shadow p-2 rounded"
                                      onClick={() => chooseImage(index)}>
            <div className="mt-2 bg-black h-48 w-full flex justify-center items-center">
                <img src={item.thumbnailSrc} alt={item.name} className="min-h-48 rounded"/>
            </div>
            <div className="mt-2 flex justify-center items-center">
                {item.description}
            </div>
            <div
                className="absolute top-0 left-0 h-full w-full flex justify-center items-center text-white/50  transition-colors hover:text-red-500/75">
                <div
                    className={"rounded-full bg-black/75 w-12 aspect-square flex justify-center items-center text-2xl"}>
                    <FontAwesomeIcon icon={solid("play")}/>
                </div>
            </div>
        </div>
    )}
</div>

const ImageTable = ({images, chooseImage}: ImagesViewProps) => <div className="grid grid-cols-20 gap-x-4 gap-y-2">
    <div className="col-span-1"></div>
    <div className="col-span-13 text-3xl font-bold">Видео</div>
    <div className="col-span-6 text-3xl font-bold">Действие</div>
    {images.map((value, index) => (
        <>
            <div className="col-span-1 flex justify-end items-center text-2xl">{index + 1}</div>
            <div className="col-span-13 flex items-center">
                <img src={value.thumbnailSrc} alt={value.name} className="w-48 rounded cursor-pointer"
                     onClick={() => chooseImage(index)}/>
                <p className="ml-4 mr-32 text break-all text-2xl">{value.name}</p>
            </div>
            <div className="col-span-6 flex items-center text-2xl">{value.description}</div>
        </>
    ))}
</div>

export function Result() {
    const nav = useNavigate();
    const [chosenImage, setChosenImage] = useState<number | null>(null);
    const [viewMode, setViewMode] = useState<ViewMode>("ChupChupChup")
    const [filter, _setFilter] = useState(Object.fromEntries(xuy.map(value => [value, false])))
    const allCbRef = useRef<HTMLInputElement>(null)
    const loadedData = useLoaderData() as Data | null

    const [allCbState, setAllCbState] = useState({
        checked: false,
        indeterminate: false,
    })


    if (allCbRef.current) {
        // allCbRef.current.checked = allCbState.checked
        allCbRef.current.indeterminate = allCbState.indeterminate
    }

    const setFilter = (upd: (prevState: { [p: string]: boolean }) => { [p: string]: boolean }) => {
        _setFilter(prevState => {
            const newFilter = upd(prevState);
            if (!allCbRef.current) return newFilter
            const x = Object.entries(newFilter).filter(value => loadedData && value[0] in loadedData);
            if (x.every(v => v[1])) {
                setAllCbState({
                    checked: true,
                    indeterminate: false
                })
            } else if (x.every(v => !v[1])) {
                setAllCbState({
                    checked: false,
                    indeterminate: false
                })
            } else {
                setAllCbState({
                    checked: false,
                    indeterminate: true
                })
            }
            return newFilter
        })
    }


    if (!loadedData) return <Navigate to="/" replace/>

    const result = [] as Item[]
    for (const key in loadedData) {
        if (!allCbState.indeterminate || filter[key])
            result.push(...loadedData[key].map(value => ({
                videoSrc: `http://localhost:8000/media/${value}`,
                thumbnailSrc: `http://localhost:8000/media/${value.replace(".mp4", ".jpg")}`,
                name: value.replace(".mp4", ".avi"),
                description: l10n[key],
                originalTag: key,
            })))
    }
    const images = result.sort((a, b) => a.name.localeCompare(b.name))


    return <div className="App">
        <div className="Result">
            <div className="result-header">
                <span className="leave-btn" onClick={() => nav("/")}><FontAwesomeIcon className="leave-icon"
                                                                                      icon={solid("arrow-right-from-bracket")}/> Выход</span>
                {/*<p>Нырок</p>*/}
                <div className="buttons-container">
                    <div className="logo-container">
                        <div className={clsx("logo my-shadow", viewMode === "ChupChupChup" ? "logo-active" : "")}
                             onClick={() => setViewMode("ChupChupChup")}>
                            <ChupChupChup/>
                        </div>
                        <div className={clsx("logo my-shadow", viewMode === "BurgZurgGurg" ? "logo-active" : "")}
                             onClick={() => setViewMode("BurgZurgGurg")}>
                            <BurgZurgGurg/>
                        </div>
                    </div>
                    <a href="#" onClick={() => downloadFile("/media/submission.csv", "submission.csv")}><FontAwesomeIcon
                        icon={solid("download")}/>Скачать CSV</a>
                </div>
            </div>
            {chosenImage !== null ? <Player chosenImage={chosenImage} close={() => setChosenImage(null)}
                                            next={() => setChosenImage(chosenImage + 1)}
                                            prev={() => setChosenImage(chosenImage - 1)}
                                            data={result}/> :
                <div className="grid grid-cols-6">
                    <div className="col-span-1 bg-white rounded m-4 my-shadow p-4">
                        <h1 className="text-4xl font-bold">Действия</h1>
                        <div className="inline-block text-2xl relative">
                            <input type="checkbox" id={`cb-all`} ref={allCbRef} checked={allCbState.checked} onChange={event => {
                                setFilter(() => Object.fromEntries(xuy.map(value => [value, event.target.checked])))
                            }}/>
                            <label htmlFor={`cb-all`}> Все</label>
                        </div>

                        {xuy.filter(value => value in loadedData).map((value, index) => (
                            <div className="ml-4 text-2xl" key={value}>
                                <input type="checkbox" id={`cb-${index}`} checked={filter[value]} onChange={(e) => {
                                    setFilter(prevState => ({
                                        ...prevState,
                                        [value]: e.target.checked,
                                    }))
                                }}/>
                                <label htmlFor={`cb-${index}`}> {l10n[value]}</label>
                            </div>
                        ))}
                    </div>
                    <div className="col-span-5 mt-4">
                        {
                            viewMode === "ChupChupChup" ?
                                <ImageTable images={images} chooseImage={setChosenImage}/> :
                                <ImageGrid images={images} chooseImage={setChosenImage}/>
                        }
                    </div>
                </div>
            }
        </div>
    </div>;
}