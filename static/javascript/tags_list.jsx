

function ListTags(props) {
    const [tags, setTags] = React.useState(props.tags);

    const handleEditButton = (tagId) => {
        window.location.href = `/tags/edit/${tagId}`;
    };

    const handleDeleteButton = (tagId) => {
        fetch(`${baseUrl}tags/delete/${tagId}`, {
            method: 'POST'
        })
        setTags(previous => previous.filter(tag => tag.tag_id !== tagId))
    };

    const handleNewTagButton = () => {
        window.location.href = `/tags/new`;
    };

    return (
        <div>
            <div className={"tags-list-title"}>
            <h1> tags list </h1>
            </div>
            <ul className={"tag-table"}>
                {tags.map(tag => (
                    <div className={"each-tag-row"} key={tag.tag_id}>
                        id: {tag.tag_id} label: {tag.label}
                        <button className={"tag-button"} onClick={() => handleEditButton(tag.tag_id)}> Edit </button>
                        <button className={"tag-button"} onClick={() => handleDeleteButton(tag.tag_id)}> Delete </button>
                    </div>
                ))}
            </ul>
            <div className={"new-tag-button"}>
                <button onClick={() => handleNewTagButton()} > New tag </button>
            </div>
        </div>
    );

}

const container = document.getElementById('root');
if (container) {
    try {
        const allTags = window.allTags;
        const baseUrl = window.baseUrl;
        const root = ReactDOM.createRoot(container);
        root.render(<ListTags tags={allTags} baseUrl={baseUrl} />);
    } catch (error) {
        console.error(error);
    }
}