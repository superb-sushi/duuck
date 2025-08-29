import CloseIcon from '../../assets/close.png';

interface Option {
  id: number;
  desc: string;
  moneyGoal: number;
  moneyCurrent: number;
}


const VoteModal = ({creatorEmail, displayed, toggleDisplay}: {creatorEmail: string, displayed: boolean, toggleDisplay: () => void}) => {

    return (
        <view className={displayed ? "option-donate-modal" : "hidden"} style="position: relative;">
            <view className="modal-island">
                <view className="modal-progress">
                    <view className="modal-btn-container">
                        <view className="modal-cancel-btn" bindtap={toggleDisplay}>
                            <text className="cancel-text">Cancel</text>
                        </view>
                        <view className="modal-contribute-btn" bindtap={toggleDisplay}>
                            <text className="contribute-text">Vote</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>
    )
}

export default VoteModal