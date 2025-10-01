function Card({ title, description, image }) {
    return (
        <>
            <div className='bg-[var(--neutral-dark-color)] h-[60rem] w-[50rem] rounded-[8rem] shadow-2xl pt-16'>
                <div className='flex flex-col h-full'>
                    <h3 className='text-6xl text-center text-[var(--neutral-color)] font-bold'>
                        {title}
                    </h3>
                    <p className='text-3xl text-[var(--neutral-secondary-color)] m-12 tracking-wider'>
                        {description}
                    </p>
                    <div className="flex-grow">
                        <img src={image} alt={title} className="w-full h-full object-cover rounded-b-[8rem]"/>
                    </div>
                </div>
            </div>
        </>
    )
}

export default Card