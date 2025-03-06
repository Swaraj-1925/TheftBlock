import React from 'react';
import { Paper, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  textAlign: 'center',
  color: theme.palette.text.secondary,
  height: '100%',
}));

function CardItem({ title, value }) {
  return (
    <StyledCard>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Typography variant="h4">{value}</Typography>
    </StyledCard>
  );
}

export default CardItem;