
const NewTag = () => {
        const [tagData, setTagData] = React.useState({label: ''})

    const handleEdit = (event) => {
        const {name, value} = event.target;
        setTagData({...tagData, [name]: value});
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        fetch(`http://localhost:8000/tags/new`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tagData),
        })
            .catch(error => {
                console.error(error);
            });
        window.location.href = `/tags/tags_list`;
    };

    return (
        <div>
            <h1> _('New tag') </h1>
            <form onSubmit={handleSubmit} >
                <h2> _('Label:') </h2>
                <input
                    type="text"
                    id="label"
                    name="label"
                    value={tagData.label}
                    onChange={handleEdit}
                    required
                    />
                <div>
                    <button type="submit"> _('Submit') </button>
                </div>
            </form>
        </div>
    );
}

const container = document.getElementById('root');
if (container) {
    try {
        const root = ReactDOM.createRoot(container);
        root.render(<NewTag />);
    } catch (error) {
        console.error(error);
    }
}