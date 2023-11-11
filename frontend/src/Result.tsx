import {LoaderFunctionArgs, Navigate, useLoaderData, useNavigate} from "react-router-dom";
import ImageGallery, {ReactImageGalleryItem} from "react-image-gallery";
import {ChangeEventHandler, useEffect, useRef, useState} from "react";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {solid} from "@fortawesome/fontawesome-svg-core/import.macro";
import {ChupChupChup} from "./assets/ChupChupChup";
import {BurgZurgGurg} from "./assets/BurgZurgGurg";
import clsx from "clsx";

const xuy = ["cartwheel", "catch", "clap", "climb", "dive", "draw_sword", "dribble", "fencing", "flic_flac", "golf", "handstand", "hit", "jump", "pick", "pour", "pullup", "push", "pushup", "shoot_ball", "sit", "situp", "swing_baseball", "sword_exercise", "throw"]


enum QualityTag {
    ANIMAL = "animal",
    BROKEN = "broken",
    EMPTY = "empty"
}

type ExtendedReactImageGalleryItem = ReactImageGalleryItem & { originalTag: QualityTag }

type Data = {
    [key in QualityTag]: string[]
}


export const loader = async (): Promise<Data | null> => {
    // ====== api request ========

    return {
        [QualityTag.ANIMAL]: [],
        [QualityTag.BROKEN]: [],
        [QualityTag.EMPTY]: [],
    };

    const response = await fetch("/api/do_good/", {
        method: "GET",
    })
    let x = await response.json();
    console.log(x)
    return response.ok ? x as Data : null;


}


const tagToDescription = {
    [QualityTag.ANIMAL]: "Животное",
    [QualityTag.EMPTY]: "Пусто",
    [QualityTag.BROKEN]: "С дефектом",
}

const filterToZipUrl: { [key: number]: string } = {
    0: "", // all false
    1: "/media/a.zip", // animal
    2: "/media/e.zip", // empty
    3: "/media/ae.zip", // animal empty
    4: "/media/b.zip", // broken
    5: "/media/ab.zip", // animal broken
    6: "/media/be.zip", // empty broken
    7: "/media/abe.zip", // all true
}

const getUrl = (filter: { [key in QualityTag]: boolean }) => {
    let result = 0;
    for (const key in filter) {
        if (filter[key as QualityTag]) {
            result += 1 << (key === QualityTag.ANIMAL ? 0 : key === QualityTag.EMPTY ? 1 : 2)
        }
    }
    return filterToZipUrl[result]
}


function MyInput({filter, filterState, onChangeFunc}: {
    filter: QualityTag,
    filterState: { [key in QualityTag]: boolean },
    onChangeFunc: ChangeEventHandler<HTMLInputElement>
}) {
    return <>
        <input type="checkbox" id={`cb-${filter}`} checked={filterState[filter]}
               onChange={onChangeFunc}/>
        <label htmlFor={`cb-${filter}`}>{tagToDescription[filter]}</label>
    </>;
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

type GalleryProps = {
    close: () => void;
    data: ExtendedReactImageGalleryItem[];
    chosenImage: number;
}

const Gallery = ({close, data, chosenImage}: GalleryProps) =>
    <div className="image-gallery-container">
        <button className="close-btn" onClick={close}><FontAwesomeIcon
            icon={solid("close")}/></button>
        <ImageGallery items={data} lazyLoad thumbnailPosition="left"
                      startIndex={chosenImage}/>
    </div>;

type ImageGridProps = {
    images: ExtendedReactImageGalleryItem[]
    chooseImage: (index: number) => void;
}

const ImageGrid = ({images, chooseImage}: ImageGridProps) => <div className="image-grid col-span-5">
    {images.map((item, index) => <div key={index} className="image-grid-item">
            <img src={item.thumbnail} alt={item.description} className={`thumbnail-${item.originalTag}`}
                 onClick={event => chooseImage(index)}/>
        </div>
    )}
</div>


export function Result() {
    const nav = useNavigate();
    const [chosenImage, setChosenImage] = useState(null as null | number);
    const [viewMode, setViewMode] = useState<ViewMode>("ChupChupChup")
    const [filterFunc, setFilterFunc] = useState(() => (_: ExtendedReactImageGalleryItem) => true)
    const [filter, setFilter] = useState(Object.fromEntries(xuy.map(value => [value, false])))
    const allCbRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
        return () => {
            if (!allCbRef.current) return
            const x = Object.values(filter);
            console.log(x)
            if (x.every(v => v)) {
                allCbRef.current.checked = true
                allCbRef.current.indeterminate = false
            } else if (x.every(v => !v)) {
                allCbRef.current.checked = false
                allCbRef.current.indeterminate = false
            } else {
                allCbRef.current.checked = false
                allCbRef.current.indeterminate = true
            }
        };
    }, [filter]);


    const loadedData = useLoaderData() as Data | null

    if (!loadedData) return <Navigate to="/" replace/>

    const changeFilterCheckbox: ChangeEventHandler<HTMLInputElement> = (e) => {
        const value = e.target.id.slice(3) as QualityTag;
        const newFilter = {
            ...filter,
            [value]: e.target.checked,
        };
        setFilterFunc(() => (item: ExtendedReactImageGalleryItem) => {
            return newFilter[item.originalTag as QualityTag]
        })
        setFilter(newFilter)
        setChosenImage(null)
    }

    const result = [] as ExtendedReactImageGalleryItem[]
    for (const key in loadedData) {
        result.push(...loadedData[key as QualityTag].map(value => ({
            original: value,
            thumbnail: value,
            originalHeight: 750,
            description: tagToDescription[key as QualityTag],
            originalTag: key as QualityTag,
            thumbnailClass: `thumbnail-${key}`,
            originalClass: `original-${key}`,
        })))
    }
    const images = result.sort((a, b) => a.original.localeCompare(b.original))


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
                        icon={solid("download")}/>Скачать отчёт</a>
                </div>
            </div>
            {chosenImage !== null ? <Gallery chosenImage={chosenImage} close={() => setChosenImage(null)}
                                             data={result.filter(filterFunc)}/> :
                <div className="grid grid-rows-6">
                    <div className="col-span-1 bg-white rounded m-4 my-shadow p-4">
                        <h1 className="text-xl font-bold">Действия</h1>
                        <div className="inline-block relative">
                            <input type="checkbox" id={`cb-all`} ref={allCbRef}/>
                            <label htmlFor={`cb-all`}> Все</label>
                        </div>

                        {xuy.map((value, index) => (
                            <div className="ml-4" key={value}>
                                <input type="checkbox" id={`cb-${index}`} checked={filter[value]} onChange={(e) => {
                                    setFilter(prevState => ({
                                        ...prevState,
                                        [value]: e.target.checked,
                                    }))
                                }}/>
                                <label htmlFor={`cb-${index}`}> {value}</label>
                            </div>
                        ))}
                    </div>
                    <ImageGrid images={images.filter(filterFunc)} chooseImage={setChosenImage}/>
                </div>
            }
        </div>
    </div>;
}