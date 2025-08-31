import CloseIcon from '../../assets/close.png';

interface Option {
  id: number;
  desc: string;
  moneyGoal: number;
  moneyCurrent: number;
}


const OptionDonateModal = ({option, displayed, setDisplayed}: {option: Option, displayed: boolean, setDisplayed: (op: Option) => void}) => {

    return (
        <view className={displayed ? "option-donate-modal" : "hidden"} style="position: relative;">
            <view className="modal-island">
                <view style="width: 100%; display: flex; justify-content: flex-end;">
                    <view bindtap={() => setDisplayed(option)}>
                        <image src={CloseIcon} className="modal-exit-icon" />
                    </view>
                </view>
                <view className="modal-header-container">
                    <text className="modal-header">Contribute to Challenge</text>
                    <text className="modal-desc">{option.desc}</text>
                </view>
                <view className="modal-progress">
                    <view className="amt">
                        <view className="modal-goal-amt-container">
                            <text className="modal-curr-amt">${option.moneyCurrent}</text>
                            <text className="modal-money-delimiter">/</text>
                            <text className="modal-goal-amt">${option.moneyGoal}</text>
                        </view>
                        <text className="progress">{((option.moneyCurrent / option.moneyGoal) * 100).toFixed(0)}% reached!</text>
                    </view>
                    <view className="modal-contribution-container">
                        <text className="modal-contribution-title">Contribution Amount</text>
                        <view className="modal-input-box"/>
                        <text className="modal-max-amt">Maximum: ${option.moneyGoal - option.moneyCurrent}</text>
                    </view>
                    <view className="modal-btn-container">
                        <view className="modal-cancel-btn" bindtap={() => setDisplayed(option)}>
                            <text className="cancel-text">Cancel</text>
                        </view>
                        <view className="modal-contribute-btn"  bindtap={() => setDisplayed(option)}>
                            <text className="contribute-text">Contribute</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>
    )
}

export default OptionDonateModal